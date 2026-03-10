# backend/main.py
import httpx
import csv
import io
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from openai import OpenAI

from .database import SessionLocal, Word

# ==========================================
# ⚠️ 在这里填入你的 DeepSeek API Key
# ==========================================
DEEPSEEK_API_KEY = "sk-f270d36ca67e43278ab9a501e40d4676"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
# ==========================================

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WordPreview(BaseModel):
    word: str;
    meaning: str;
    chinese_meaning: str;
    phonetic: str;
    audio_url: str;
    examples: str


class ReviewSubmit(BaseModel): quality: int


class WordUpdate(BaseModel): chinese_meaning: str


class AIQuery(BaseModel): word: str; question: str


class AIChatQuery(BaseModel): question: str  # 新增：全局聊天的请求体


# 1. 查词与录入
@app.get("/api/search/{word}")
async def search_word(word: str):
    word_str = word.strip().lower()
    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_str}")
    if response.status_code != 200: raise HTTPException(status_code=404, detail="未找到该单词")
    data = response.json()[0]
    phonetic = data.get("phonetic", "")
    audio_url = next((p.get("audio") for p in data.get("phonetics", []) if p.get("audio")), "")
    meaning = data.get("meanings", [{"definitions": [{"definition": ""}]}])[0]["definitions"][0].get("definition", "")
    example = data.get("meanings", [{"definitions": [{"example": ""}]}])[0]["definitions"][0].get("example", "")
    try:
        chinese_meaning = GoogleTranslator(source='en', target='zh-CN').translate(word_str)
    except:
        chinese_meaning = "翻译失败"
    return {"word": word_str, "meaning": meaning, "chinese_meaning": chinese_meaning, "phonetic": phonetic,
            "audio_url": audio_url, "examples": example}


@app.post("/api/words")
def save_word(item: WordPreview, db: Session = Depends(get_db)):
    if db.query(Word).filter(Word.word == item.word).first(): raise HTTPException(status_code=400, detail="已在词库中")
    db.add(Word(**item.dict(), next_review_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')));
    db.commit()
    return {"message": "录入成功"}


# 2. 智能复习
@app.get("/api/words/due")
def get_due_words(limit: int = Query(15, ge=1, le=100), db: Session = Depends(get_db)):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. 优先获取真正到期的单词（按掌握度 EF 从低到高排，最难的先出）
    due_words = db.query(Word).filter(Word.next_review_date <= now_str).order_by(Word.easiness_factor.asc()).limit(
        limit).all()

    # 2. 【核心改进】如果到期的单词不够，启动“动态强化机制”兜底
    if len(due_words) < limit:
        shortage = limit - len(due_words)
        # 获取已经选出的单词 ID，避免重复抽取
        due_word_ids = [w.id for w in due_words]

        # 从剩下的所有单词里，挑选出 EF 值最低（你最不熟悉）的单词来填补空缺
        extra_words = db.query(Word) \
            .filter(~Word.id.in_(due_word_ids)) \
            .order_by(Word.easiness_factor.asc(), Word.repetition.asc()) \
            .limit(shortage).all()

        due_words.extend(extra_words)

    return due_words


@app.put("/api/words/{word_id}/review")
def review_word(word_id: int, review: ReviewSubmit, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    q, now = review.quality, datetime.now()
    if q == 0:
        word.interval, word.repetition, word.next_review_date = 0, 0, (now + timedelta(minutes=5)).strftime(
            '%Y-%m-%d %H:%M:%S')
    elif q == 2:
        word.interval, word.next_review_date = 0, (now + timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        word.interval = 1 if word.repetition == 0 else (
            6 if word.repetition == 1 else int(max(1, word.interval * word.easiness_factor)))
        word.repetition += 1
        word.next_review_date = (now + timedelta(days=word.interval)).strftime('%Y-%m-%d %H:%M:%S')
    word.easiness_factor = max(1.3, word.easiness_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    db.commit()
    return {"message": "已记录"}


# 3. 数据与管理
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"total": db.query(Word).count(),
            "pending_now": db.query(Word).filter(Word.next_review_date <= now_str).count(),
            "mastered": db.query(Word).filter(Word.easiness_factor > 2.6).count()}


@app.get("/api/words/all")
def get_all_words(db: Session = Depends(get_db)): return db.query(Word).order_by(Word.id.desc()).all()


@app.delete("/api/words/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)): db.query(Word).filter(
    Word.id == word_id).delete(); db.commit()


@app.put("/api/words/{word_id}")
def update_word(word_id: int, item: WordUpdate, db: Session = Depends(get_db)): db.query(Word).filter(
    Word.id == word_id).update({"chinese_meaning": item.chinese_meaning}); db.commit()


@app.get("/api/words/export")
def export_words(db: Session = Depends(get_db)):
    stream = io.StringIO();
    writer = csv.writer(stream, dialect="excel")
    writer.writerow(["单词", "音标", "精简释义", "掌握度", "下次复习"]);
    [writer.writerow([w.word, w.phonetic, w.chinese_meaning, round(w.easiness_factor, 2), w.next_review_date]) for w in
     db.query(Word).all()]
    stream.seek(0)
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=vocabulary.csv"})


# ==========================================
# 4. DeepSeek AI 接口区
# ==========================================

# 4.1 单个单词讲解私教 (原有功能)
@app.post("/api/ai/tutor")
async def ai_tutor(query: AIQuery):
    try:
        prompt = f"学生遇到生词 '{query.word}'。诉求：{query.question}。请用简明通俗的中文回答，重点提供：1. 词根词缀或谐音记忆法；2. 给出 1-2 个该词的高频搭配或短语。"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是一名幽默且经验丰富的英语专家。"},
                      {"role": "user", "content": prompt}],
            max_tokens=500, temperature=0.7
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        return {"answer": f"AI 私教暂时开小差了。错误详情: {str(e)}"}


# 4.2 🌟全局词库智能对话 (本次新增核心功能)
@app.post("/api/ai/chat")
async def ai_global_chat(query: AIChatQuery, db: Session = Depends(get_db)):
    try:
        # 步骤 1：从数据库拉取用户的全量词汇
        words = db.query(Word).all()
        if not words:
            return {"answer": "你的词库目前还是空的哦，请先去【录入】界面添加一些单词，再来问我吧！"}

        # 步骤 2：组装词库上下文 (为了节省 token，只提取单词和释义)
        vocab_list = "\n".join([f"- {w.word} ({w.chinese_meaning})" for w in words])

        # 步骤 3：构建带有强大上下文的 Prompt
        prompt = f"""
        你是一位专业的英语辅导专家。以下是该学生目前专属词库中的所有单词：

        {vocab_list}

        学生的指令/问题是：【{query.question}】

        请严格基于上述词库列表来回答学生的问题。如果学生要求分类、总结或造句，请尽量多使用词库中的单词。使用清晰、有条理的 Markdown 格式输出。
        """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个高度智能的词汇分析助手，擅长对单词进行分类、归纳、对比和记忆指导。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6  # 偏向逻辑分析，降低发散性
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        return {"answer": f"全局分析失败，请检查网络或 API 配置。错误详情: {str(e)}"}