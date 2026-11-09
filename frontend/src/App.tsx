import { Link, Outlet } from 'react-router'
import { PwaStatus } from './components/PwaStatus'

export function App() {
  return (
    <>
      <PwaStatus />
      <nav className="topbar">
        <Link to="/" className="brand">
          ValueTech <strong>LMS</strong>
        </Link>
      </nav>
      <main className="container">
        <Outlet />
      </main>
    </>
  )
}
