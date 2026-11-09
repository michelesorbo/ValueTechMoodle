import { useQuery } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { api } from '../api/client'
import { ScormPlayer } from '../components/ScormPlayer'

export function PlayerPage() {
  const { packageId = '' } = useParams()
  const navigate = useNavigate()
  const [lastCommit, setLastCommit] = useState<Date | null>(null)

  const launch = useQuery({
    queryKey: ['launch', packageId],
    queryFn: () => api.launchPackage(packageId),
    // Il launch crea/riprende un tentativo: non va rifatto in background
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  })

  const onCommit = useCallback(() => setLastCommit(new Date()), [])

  if (launch.isPending) return <p className="muted">Preparazione del contenuto…</p>
  if (launch.error) return <p className="error">{launch.error.message}</p>

  return (
    <section className="player">
      <header className="row">
        <button className="ghost" onClick={() => void navigate(-1)}>
          ← Esci
        </button>
        <span className="muted">
          SCORM {launch.data.version}
          {lastCommit && ` · salvato alle ${lastCommit.toLocaleTimeString('it-IT')}`}
        </span>
      </header>
      <ScormPlayer launch={launch.data} onCommit={onCommit} />
    </section>
  )
}
