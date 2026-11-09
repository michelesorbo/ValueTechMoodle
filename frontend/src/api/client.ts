export type ScormVersion = '1.2' | '2004'

export interface Course {
  id: string
  code: string
  title: string
  description: string | null
  is_published: boolean
  created_at: string
  updated_at: string
}

export interface CourseCreate {
  code: string
  title: string
  description?: string | null
  is_published?: boolean
}

export interface ScormPackage {
  id: string
  course_id: string
  title: string
  version: ScormVersion
  launch_path: string
  created_at: string
}

export interface ScormLaunch {
  package_id: string
  attempt_id: string
  version: ScormVersion
  launch_url: string
  commit_url: string
  cmi: Record<string, unknown>
  learner_id: string
  learner_name: string
}

export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `HTTP ${status}`)
    this.status = status
    this.detail = detail
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    credentials: 'include',
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.body && !(init.body instanceof FormData)
        ? { 'Content-Type': 'application/json' }
        : {}),
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const body: unknown = await res.json().catch(() => null)
    const detail =
      body && typeof body === 'object' && 'detail' in body ? (body as { detail: unknown }).detail : body
    throw new ApiError(res.status, detail)
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}

export const api = {
  listCourses: () => request<Course[]>('/courses'),
  getCourse: (id: string) => request<Course>(`/courses/${id}`),
  createCourse: (payload: CourseCreate) =>
    request<Course>('/courses', { method: 'POST', body: JSON.stringify(payload) }),
  listPackages: (courseId: string) => request<ScormPackage[]>(`/courses/${courseId}/packages`),
  uploadPackage: (courseId: string, file: File) => {
    const form = new FormData()
    form.append('course_id', courseId)
    form.append('file', file)
    return request<ScormPackage>('/scorm/packages', { method: 'POST', body: form })
  },
  launchPackage: (packageId: string) => request<ScormLaunch>(`/scorm/packages/${packageId}/launch`),
}
