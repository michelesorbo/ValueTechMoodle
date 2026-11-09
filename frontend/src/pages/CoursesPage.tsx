import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../api/client'

export function CoursesPage() {
  const qc = useQueryClient()
  const courses = useQuery({ queryKey: ['courses'], queryFn: api.listCourses })
  const [code, setCode] = useState('')
  const [title, setTitle] = useState('')

  const create = useMutation({
    mutationFn: api.createCourse,
    onSuccess: () => {
      setCode('')
      setTitle('')
      void qc.invalidateQueries({ queryKey: ['courses'] })
    },
  })

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    create.mutate({ code, title })
  }

  return (
    <section>
      <h1>Corsi</h1>

      <form className="card form-inline" onSubmit={onSubmit}>
        <input
          placeholder="Codice (es. AI-01)"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
          pattern="[A-Za-z0-9_\-]+"
        />
        <input
          placeholder="Titolo del corso"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <button disabled={create.isPending}>Crea corso</button>
        {create.error && <p className="error">{create.error.message}</p>}
      </form>

      {courses.isPending && <p className="muted">Caricamento…</p>}
      {courses.error && <p className="error">{courses.error.message}</p>}
      {courses.data?.length === 0 && <p className="muted">Nessun corso. Creane uno!</p>}

      <ul className="grid">
        {courses.data?.map((c) => (
          <li key={c.id} className="card">
            <span className="badge">{c.code}</span>
            <h2>
              <Link to={`/courses/${c.id}`}>{c.title}</Link>
            </h2>
            <p className="muted">{c.is_published ? 'Pubblicato' : 'Bozza'}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}
