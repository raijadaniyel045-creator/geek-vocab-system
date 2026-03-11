<template>
  <div>
    <NavBarComponent/>
    <div id="spacer"></div>
    <section class="graph">
      <div class="word-add">
        <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
          <UFormField label="Word" name="word">
            <UInput v-model="state.word" type="text" />
          </UFormField>
          <UButton type="submit">
            Submit
          </UButton>
        </UForm>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import * as v from 'valibot';
import { reactive } from 'vue';
import type { FormSubmitEvent } from '@nuxt/ui';

type SearchWorldModel = {
  word : string;
}

const schema = v.object({
  word: v.pipe(v.string())
});

type Schema = v.InferOutput<typeof schema>
const state = reactive<SearchWorldModel>({
  word: ''
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
  console.log(event.data);
}
</script>

<style scoped>

#spacer {
  height: 30vh;
}

.graph {
  position: relative;
  top: 100%;
  width: 100%;
  padding-top: 80px;
  padding-bottom: 100px;
  font-size: 0;
  text-align: center;
  transition: .25s
}

.word-add {
  display: flex;
  flex-direction: column;
}
</style>