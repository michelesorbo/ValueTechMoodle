import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, api } from './client'

describe('api client', () => {
  afterEach(() => vi.restoreAllMocks())

  it('chiama /api/courses e restituisce il JSON', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify([{ id: '1' }]), { status: 200 }))

    const data = await api.listCourses()

    expect(data).toEqual([{ id: '1' }])
    expect(fetchMock).toHaveBeenCalledWith('/api/courses', expect.objectContaining({ credentials: 'include' }))
  })

  it('mappa gli errori FastAPI (detail) in ApiError', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Codice corso già esistente' }), { status: 409 }),
    )

    const err = await api.createCourse({ code: 'X', title: 'Y' }).catch((e: unknown) => e)
    expect(err).toBeInstanceOf(ApiError)
    expect((err as ApiError).status).toBe(409)
    expect((err as ApiError).message).toBe('Codice corso già esistente')
  })

  it('non imposta Content-Type JSON per upload multipart', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response('{}', { status: 201 }))

    await api.uploadPackage('c1', new File(['x'], 'p.zip'))

    const init = fetchMock.mock.calls[0]![1]!
    expect(init.body).toBeInstanceOf(FormData)
    expect((init.headers as Record<string, string>)['Content-Type']).toBeUndefined()
  })
})
