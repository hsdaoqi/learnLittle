import { useEffect, useRef, useState } from 'react'
import { knowledgeApi } from '../api/knowledge'
import { ApiError } from '../api/client'
import type { KnowledgeDocument, KnowledgeSearchHit } from '../types/knowledge'

interface UploadProgress {
  id: string
  filename: string
  progress: number
  stage: string
  status: 'uploading' | 'completed' | 'error'
  message?: string
}

const STAGE_LABEL: Record<string, string> = {
  saving: '保存文件',
  saved: '已保存',
  parsing: '解析文档',
  parsed: '解析完成',
  splitting: '文本切片',
  splitted: '切片完成',
  vectorizing: '写入向量',
  vectorized: '向量入库完成',
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function KnowledgeBasePage() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploads, setUploads] = useState<UploadProgress[]>([])
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [query, setQuery] = useState('')
  const [hits, setHits] = useState<KnowledgeSearchHit[]>([])
  const [searching, setSearching] = useState(false)

  async function load() {
    setLoading(true)
    setError('')
    try {
      const data = await knowledgeApi.list()
      setDocuments(data.documents)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleFiles(files: FileList | File[]) {
    const list = Array.from(files)
    if (list.length === 0) return
    setUploading(true)
    setError('')
    try {
      for (const file of list) {
        const localId = `${file.name}-${Date.now()}-${Math.random().toString(16).slice(2)}`
        setUploads((prev) => [
          ...prev,
          { id: localId, filename: file.name, progress: 0, stage: '准备上传', status: 'uploading' },
        ])
        try {
          await knowledgeApi.upload(file, {
            onProcessing: (event) => {
              setUploads((prev) =>
                prev.map((item) =>
                  item.id === localId
                    ? {
                        ...item,
                        progress: event.progress ?? item.progress,
                        stage: STAGE_LABEL[event.stage || ''] || event.message || item.stage,
                      }
                    : item,
                ),
              )
            },
            onCompleted: () => {
              setUploads((prev) =>
                prev.map((item) =>
                  item.id === localId
                    ? { ...item, progress: 100, status: 'completed', stage: '完成' }
                    : item,
                ),
              )
            },
            onError: (message) => {
              setUploads((prev) =>
                prev.map((item) =>
                  item.id === localId ? { ...item, status: 'error', message } : item,
                ),
              )
            },
          })
        } catch (err) {
          const message = err instanceof ApiError ? err.message : '上传失败'
          setUploads((prev) =>
            prev.map((item) =>
              item.id === localId ? { ...item, status: 'error', message } : item,
            ),
          )
          setError(message)
        }
      }
      await load()
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm('删除后文件和向量都无法恢复，确定吗？')) {
      return
    }
    await knowledgeApi.remove(id)
    await load()
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-gray-200 bg-white px-4 py-3">
        <h1 className="text-base font-semibold">知识库</h1>
        <p className="mt-1 text-xs text-gray-400">
          上传后会解析、切片并写入本地向量库。支持 PDF / Markdown / TXT，单文件 50MB。
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {error && <p className="mb-3 text-sm text-red-500">{error}</p>}

        <form
          className="mb-6 flex gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            void (async () => {
              if (!query.trim()) return
              setSearching(true)
              setError('')
              try {
                const data = await knowledgeApi.search(query.trim())
                setHits(data.items)
              } catch (err) {
                setError(err instanceof ApiError ? err.message : '检索失败')
              } finally {
                setSearching(false)
              }
            })()
          }}
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="在已上传文档里检索"
            className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={searching}
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {searching ? '检索中…' : '检索'}
          </button>
        </form>

        {hits.length > 0 && (
          <ul className="mb-6 space-y-2">
            {hits.map((hit, idx) => (
              <li key={`${hit.document_id}-${hit.chunk_index}-${idx}`} className="rounded-xl bg-white p-4 shadow-card">
                <p className="text-xs text-gray-400">
                  {hit.filename}
                  {hit.section_title ? ` · ${hit.section_title}` : ''}
                  {' · '}
                  {(hit.score * 100).toFixed(0)}%
                </p>
                <p className="mt-1 whitespace-pre-wrap text-sm text-gray-800">{hit.content}</p>
              </li>
            ))}
          </ul>
        )}

        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragOver(true)
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragOver(false)
            void handleFiles(e.dataTransfer.files)
          }}
          onClick={() => inputRef.current?.click()}
          className={`mb-6 cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${
            dragOver
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-gray-300 bg-white hover:border-indigo-400'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.md,.markdown"
            className="hidden"
            onChange={(e) => {
              if (e.target.files) void handleFiles(e.target.files)
              e.target.value = ''
            }}
          />
          <p className="text-sm text-gray-600">
            {uploading ? '正在上传…' : '点击或拖拽文件到这里上传'}
          </p>
          <p className="mt-1 text-xs text-gray-400">PDF / Markdown / TXT</p>
        </div>

        {uploads.length > 0 && (
          <div className="mb-6 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700">上传进度</p>
              <button
                type="button"
                className="text-xs text-gray-400 hover:text-gray-600"
                onClick={() => setUploads((prev) => prev.filter((item) => item.status === 'uploading'))}
              >
                清除已完成
              </button>
            </div>
            {uploads.map((item) => (
              <div key={item.id} className="rounded-xl bg-white p-3 shadow-card">
                <div className="flex items-center justify-between text-sm">
                  <span className="truncate font-medium">{item.filename}</span>
                  <span
                    className={
                      item.status === 'error'
                        ? 'text-xs text-red-500'
                        : item.status === 'completed'
                          ? 'text-xs text-green-600'
                          : 'text-xs text-gray-400'
                    }
                  >
                    {item.status === 'error' ? item.message || '失败' : `${item.progress}%`}
                  </span>
                </div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-gray-100">
                  <div
                    className={`h-full ${item.status === 'error' ? 'bg-red-400' : 'bg-indigo-500'}`}
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-gray-400">{item.stage}</p>
              </div>
            ))}
          </div>
        )}

        {loading && <p className="text-sm text-gray-400">加载中…</p>}
        {!loading && documents.length === 0 && (
          <p className="text-sm text-gray-400">还没有文档，先上传一份作为 RAG 的原料。</p>
        )}
        <ul className="space-y-2">
          {documents.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between rounded-xl bg-white p-4 shadow-card"
            >
              <div className="min-w-0">
                <p className="truncate font-medium">{doc.filename}</p>
                <p className="mt-1 text-xs text-gray-400">
                  {formatSize(doc.file_size)} · {doc.chunk_count} 个切片 · {doc.file_type}
                  {' · '}
                  {new Date(doc.created_at).toLocaleString('zh-CN')}
                </p>
              </div>
              <button
                className="ml-3 shrink-0 rounded px-2 py-1 text-xs text-red-500 hover:bg-red-50"
                onClick={() => void handleDelete(doc.id)}
              >
                删除
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
