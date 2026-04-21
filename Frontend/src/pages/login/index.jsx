import { useState } from 'react'
import '../../styles/account-pages.css'
import { ApiError } from '../../services/portal-api'
import { fetchCurrentUser, loginWithPassword } from '../../services/auth-api'

function LoginPage({ onAuthChange, onChangePage }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')

  const handleChange = (field) => (event) => {
    setFormData((current) => ({
      ...current,
      [field]: event.target.value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus('loading')
    setMessage('')

    try {
      await loginWithPassword(formData)
      const user = await fetchCurrentUser()
      onAuthChange(user)
      setStatus('success')
      setMessage('Login realizado com sucesso.')
      onChangePage('home')
    } catch (error) {
      setStatus('error')
      setMessage(
        error instanceof ApiError
          ? error.message
          : 'Nao foi possivel fazer login agora.',
      )
    }
  }

  return (
    <section className="account-page">
      <div className="page-lead">
        <p className="story-kicker">Login</p>
        <h1>Entre para retomar sua leitura, seus alertas e os destaques do portal.</h1>
        <p>
          A pagina de login faz parte da experiencia principal do Nexus IA e
          prepara o acesso a favoritos, preferencias editoriais e leitura personalizada.
        </p>
      </div>

      <div className="account-grid">
        <form className="account-card" onSubmit={handleSubmit}>
          <h2>Acessar conta</h2>
          <label>
            E-mail
            <input
              type="email"
              placeholder="voce@nexus.ai"
              value={formData.email}
              onChange={handleChange('email')}
              required
            />
          </label>
          <label>
            Senha
            <input
              type="password"
              placeholder="Sua senha"
              value={formData.password}
              onChange={handleChange('password')}
              required
            />
          </label>
          {message ? (
            <p className={status === 'error' ? 'account-message is-error' : 'account-message is-success'}>
              {message}
            </p>
          ) : null}
          <button className="submit-button" type="submit">
            {status === 'loading' ? 'Entrando...' : 'Entrar'}
          </button>
          <button className="ghost-button" type="button">
            Esqueci minha senha
          </button>
        </form>

        <aside className="benefit-panel">
          <h2>Ao entrar, voce encontra</h2>
          <ul>
            <li>Historico de leitura e materias salvas</li>
            <li>Preferencias de categorias e tags</li>
            <li>Acesso rapido aos destaques e analises do portal</li>
            <li>Area pronta para dashboard editorial e revisao</li>
          </ul>
          <button className="inline-button" type="button" onClick={() => onChangePage('register')}>
            Criar conta
          </button>
        </aside>
      </div>
    </section>
  )
}

export default LoginPage
