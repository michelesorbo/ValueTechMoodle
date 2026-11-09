import { useEffect, useRef } from 'react'
import { Scorm12API } from 'scorm-again/scorm12'
import { Scorm2004API } from 'scorm-again/scorm2004'
import type { ScormLaunch } from '../api/client'

type ScormApi = Scorm12API | Scorm2004API

declare global {
  interface Window {
    API?: Scorm12API
    API_1484_11?: Scorm2004API
  }
}

interface Props {
  launch: ScormLaunch
  onCommit?: () => void
}

/**
 * Espone l'API runtime SCORM sul window del parent e carica lo SCO in un iframe.
 *
 * Lo SCO cerca `window.parent.API` (1.2) o `window.parent.API_1484_11` (2004): per
 * questo contenuti SCORM e app devono essere serviti dallo STESSO origin.
 */
export function ScormPlayer({ launch, onCommit }: Props) {
  const frameRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    const settings = {
      lmsCommitUrl: launch.commit_url,
      autocommit: true,
      autocommitSeconds: 30,
      dataCommitFormat: 'json',
      xhrWithCredentials: true,
      logLevel: import.meta.env.DEV ? 'DEBUG' : 'ERROR',
    } as const

    const isScorm12 = launch.version === '1.2'
    const api: ScormApi = isScorm12 ? new Scorm12API(settings) : new Scorm2004API(settings)

    if (Object.keys(launch.cmi).length > 0) {
      // Ripristino del tentativo precedente (suspend_data, location, status, ...)
      api.loadFromJSON(launch.cmi)
    }
    const learner = isScorm12 ? 'cmi.core.student' : 'cmi.learner'
    api.loadFromFlattenedJSON({
      [`${learner}_id`]: launch.learner_id,
      [`${learner}_name`]: launch.learner_name,
    })

    const commitEvent = isScorm12 ? 'LMSCommit' : 'Commit'
    if (onCommit) api.on(commitEvent, onCommit)

    if (isScorm12) window.API = api as Scorm12API
    else window.API_1484_11 = api as Scorm2004API

    // Lo SCO viene caricato solo DOPO che l'API è esposta sul parent
    const frame = frameRef.current
    if (frame) frame.src = launch.launch_url

    return () => {
      if (frame) frame.src = 'about:blank'
      delete window.API
      delete window.API_1484_11
    }
  }, [launch, onCommit])

  return (
    <iframe
      ref={frameRef}
      key={launch.attempt_id}
      className="scorm-frame"
      title="Contenuto SCORM"
      // allow-same-origin è necessario perché lo SCO raggiunga window.parent.API
      sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-downloads"
      allow="fullscreen; autoplay"
    />
  )
}
