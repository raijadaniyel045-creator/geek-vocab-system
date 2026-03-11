<template>
  <div>
    <NavBarComponent/>
    <div id="spacer"></div>
    <section class="graph">
      <h2>📚 词库管理</h2>
      <div class="heading-underline"/>
      <div id="words-container">
        <UTable
            ref="table"
            :columns="columns"
            :data="data"
            class="h-96"
            sticky
        >
          <template #expanded="{ row }">
            <pre>{{ row.original }}</pre>
          </template>
        </UTable>
      </div>
    </section>
  </div>
</template>

<script lang="ts" setup>
import {h, ref, resolveComponent, useTemplateRef} from 'vue'
//import { upperFirst } from 'scule'
import type {TableColumn} from '@nuxt/ui'
import {useClipboard} from '@vueuse/core'

const UButton = resolveComponent('UButton')
const UCheckbox = resolveComponent('UCheckbox')
const UInput = resolveComponent('UInput')
const UDropdownMenu = resolveComponent('UDropdownMenu')

const toast = useToast()
const {copy} = useClipboard()

type WordInfo = {
  id: string
  word: string
  definition: string
  mastery: number
}
// 单词	释义 (点击直接修改)	掌握度 (EF)	操作

const data = ref<WordInfo[]>([
  {id: "0", word: "add", definition: "add", mastery: 1},
  {id: "1", word: "remove", definition: "add", mastery: 1},
]);

const columns: TableColumn<WordInfo>[] = [
  {
    id: 'select',
    header: ({table}) => h(UCheckbox, {
      'modelValue': table.getIsSomePageRowsSelected() ? 'indeterminate' : table.getIsAllPageRowsSelected(),
      'onUpdate:modelValue': (value: boolean | 'indeterminate') => table.toggleAllPageRowsSelected(!!value),
      'aria-label': 'Select all'
    }),
    cell: ({row}) => h(UCheckbox, {
      'modelValue': row.getIsSelected(),
      'onUpdate:modelValue': (value: boolean | 'indeterminate') => row.toggleSelected(!!value),
      'aria-label': 'Select row'
    }),
    enableSorting: false,
    enableHiding: false
  },
  {
    accessorKey: 'id',
    header: '#',
    cell: ({row}) => `#${row.getValue('id')}`
  },
  {
    accessorKey: 'word',
    header: 'Word',
    cell: ({row}) => `${row.getValue('word')}`
  },
  {
    accessorKey: 'definition',
    header: 'Definition',
    cell: ({row}) => `${row.getValue('definition')}`
  },
  {
    accessorKey: 'mastery',
    header: 'Mastery',
    meta: {
      class: {
        th: 'text-right',
        td: 'text-right font-medium'
      }
    },
    cell: ({row}) => `${row.getValue<number>('mastery')*100}%`
  },
  {
    id: 'actions',
    enableHiding: false,
    meta: {
      class: {
        td: 'text-right'
      }
    },
    cell: ({row}) => {
      const items = [{
        type: 'label',
        label: 'Actions'
      }, {
        label: 'Copy payment ID',
        onSelect() {
          copy(row.original.id)

          toast.add({
            title: 'Payment ID copied to clipboard!',
            color: 'success',
            icon: 'i-lucide-circle-check'
          })
        }
      }, {
        label: row.getIsExpanded() ? 'Collapse' : 'Expand',
        onSelect() {
          row.toggleExpanded()
        }
      }, {
        type: 'separator'
      }, {
        label: 'View customer'
      }, {
        label: 'View payment details'
      }]

      return h(UDropdownMenu, {
        'content': {
          align: 'end'
        },
        items,
        'aria-label': 'Actions dropdown'
      }, () => h(UButton, {
        'icon': 'i-lucide-ellipsis-vertical',
        'color': 'neutral',
        'variant': 'ghost',
        'aria-label': 'Actions dropdown'
      }))
    }
  }]

const table = useTemplateRef('table')
</script>

<style scoped>
h2 {
  margin-top: 25px;
  font-weight: 400;
  font-size: 20px;
  color: #fff
}

.heading-underline {
  display: inline-block;
  width: 130px;
  height: 4px;
  border-radius: 2px;
  background-color: var(--theme-color);
}

#spacer {
  height: 10vh;
}

.graph {
  position: relative;
  top: 100%;
  width: 100%;
  padding-top: 80px;
  padding-bottom: 100px;
  font-size: 0;
  text-align: center;
  transition: .25s;
}

.graph.highlight {
  background-color: var(--bg-w-245);
}

#words-container {
  margin: 10px 10% 0 10%;
}

</style>