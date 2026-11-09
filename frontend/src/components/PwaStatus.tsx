import { useEffect, useState } from 'react'
import { useRegisterSW } from 'virtual:pwa-register/react'

function useOnline() {
  const [online, setOnline] = useState(() => navigator.onLine)
  useEffect(() => {
    const on = () => setOnline(true)
    const off = () => setOnline(false)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])
  return online
}

/** Banner offline + prompt di aggiornamento del service worker. */
export function PwaStatus() {
  const online = useOnline()
  const {
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW()

  return (
    <>
      {!online && (
        <div className="banner banner-warn" role="status">
          Sei offline: stai consultando dati in cache. Il tracciamento SCORM riprenderà alla
          riconnessione.
        </div>
      )}
      {needRefresh && (
        <div className="banner banner-info" role="alert">
          È disponibile una nuova versione.
          <button onClick={() => void updateServiceWorker(true)}>Aggiorna</button>
          <button className="ghost" onClick={() => setNeedRefresh(false)}>
            Più tardi
          </button>
        </div>
      )}
    </>
  )
}
