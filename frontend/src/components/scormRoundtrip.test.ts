import { describe, expect, it } from 'vitest'
import { Scorm12API } from 'scorm-again/scorm12'
import { Scorm2004API } from 'scorm-again/scorm2004'

/**
 * Verifica il contratto con il backend: il payload `cmi` salvato da /commit
 * deve poter essere ricaricato con loadFromJSON() al rilancio del pacchetto.
 */
describe('SCORM CMI round-trip', () => {
  it('SCORM 1.2: commit → persist → loadFromJSON ripristina lo stato', () => {
    const first = new Scorm12API({ logLevel: 'NONE' })
    first.LMSInitialize('')
    first.LMSSetValue('cmi.core.lesson_status', 'incomplete')
    first.LMSSetValue('cmi.core.lesson_location', 'slide-7')
    first.LMSSetValue('cmi.suspend_data', '{"q1":true}')
    const payload = first.renderCommitCMI(true) as { cmi: Record<string, unknown> }

    // Ciò che il backend salva e restituisce nel /launch
    const stored = JSON.parse(JSON.stringify(payload.cmi)) as Record<string, unknown>

    const second = new Scorm12API({ logLevel: 'NONE' })
    second.loadFromJSON(stored)
    second.LMSInitialize('')
    expect(second.LMSGetValue('cmi.core.lesson_location')).toBe('slide-7')
    expect(second.LMSGetValue('cmi.suspend_data')).toBe('{"q1":true}')
    expect(second.LMSGetValue('cmi.core.lesson_status')).toBe('incomplete')
  })

  it('SCORM 2004: commit → persist → loadFromJSON ripristina lo stato', () => {
    const first = new Scorm2004API({ logLevel: 'NONE' })
    first.Initialize('')
    first.SetValue('cmi.location', 'p3')
    first.SetValue('cmi.completion_status', 'incomplete')
    const payload = first.renderCommitCMI(true) as { cmi: Record<string, unknown> }
    const stored = JSON.parse(JSON.stringify(payload.cmi)) as Record<string, unknown>

    const second = new Scorm2004API({ logLevel: 'NONE' })
    second.loadFromJSON(stored)
    second.Initialize('')
    expect(second.GetValue('cmi.location')).toBe('p3')
    expect(second.GetValue('cmi.completion_status')).toBe('incomplete')
  })
})
