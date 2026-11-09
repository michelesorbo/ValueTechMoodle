import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type ChangeEvent } from 'react'
import { Link, useParams } from 'react-router'
import { api } from '../api/client'

export function CoursePage() {
  const { courseId = '' } = useParams()
  const qc = useQueryClient()

  const course = useQuery({ queryKey: ['courses', courseId], queryFn: () => api.getCourse(courseId) })
  const packages = useQuery({
    queryKey: ['courses', courseId, 'packages'],
    queryFn: () => api.listPackages(courseId),
  })

  const upload = useMutation({
    mutationFn: (file: File) => api.uploadPackage(courseId, file),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['courses', courseId, 'packages'] }),
  })

  const onFile = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) upload.mutate(file)
    e.target.value = ''
  }

  if (course.isPending) return <p className="muted">Caricamento…</p>
  if (course.error) return <p className="error">{course.error.message}</p>

  return (
    <section>
      <Link to="/">← Tutti i corsi</Link>
      <h1>{course.data.title}</h1>
      {course.data.description && <p>{course.data.description}</p>}

      <div className="card">
        <h2>Carica pacchetto SCORM</h2>
        <input type="file" accept=".zip,application/zip" onChange={onFile} disabled={upload.isPending} />
        {upload.isPending && <p className="muted">Caricamento e validazione in corso…</p>}
        {upload.error && <p className="error">{upload.error.message}</p>}
      </div>

      <h2>Contenuti</h2>
      {packages.data?.length === 0 && <p className="muted">Nessun pacchetto caricato.</p>}
      <ul className="list">
        {packages.data?.map((p) => (
          <li key={p.id} className="card row">
            <div>
              <strong>{p.title}</strong> <span className="badge">SCORM {p.version}</span>
            </div>
            <Link className="button" to={`/play/${p.id}`}>
              Avvia
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
