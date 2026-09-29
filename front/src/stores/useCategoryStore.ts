import { create } from 'zustand'
import { categoryApi } from '../api/category'
import { notesApi } from '../api/notes'
import { UNCATEGORIZED_SENTINEL, type Category } from '../types/notes'
import { ApiError } from '../api/client'

interface CategoryState {
  categories: Category[]
  uncategorizedCount: number
  selectedCategoryId: string | null
  loading: boolean
  error: string | null
  fetchCategories: () => Promise<void>
  selectCategory: (id: string | null) => void
  createCategory: (name: string, parentId: string | null) => Promise<void>
  renameCategory: (id: string, name: string) => Promise<void>
  deleteCategory: (id: string) => Promise<void>
}

export const useCategoryStore = create<CategoryState>((set, get) => ({
  categories: [],
  uncategorizedCount: 0,
  selectedCategoryId: null,
  loading: false,
  error: null,

  fetchCategories: async () => {
    set({ loading: true, error: null })
    try {
      const [tree, uncategorized] = await Promise.all([
        categoryApi.getTree(),
        notesApi.list({ uncategorized: true, page_size: 1 }),
      ])
      set({
        categories: tree,
        uncategorizedCount: uncategorized.total,
        loading: false,
      })
    } catch (err) {
      set({
        error: err instanceof ApiError ? err.message : '分类树加载失败',
        loading: false,
      })
    }
  },

  selectCategory: (id) => set({ selectedCategoryId: id }),

  createCategory: async (name, parentId) => {
    await categoryApi.create({ name, parent_id: parentId })
    await get().fetchCategories()
  },

  renameCategory: async (id, name) => {
    await categoryApi.update(id, { name })
    await get().fetchCategories()
  },

  deleteCategory: async (id) => {
    await categoryApi.remove(id)
    const selected = get().selectedCategoryId
    if (selected === id) set({ selectedCategoryId: null })
    await get().fetchCategories()
  },
}))

export { UNCATEGORIZED_SENTINEL }
