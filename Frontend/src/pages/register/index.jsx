import { useState } from 'react'
import '../../styles/account-pages.css'
import { ApiError } from '../../services/portal-api'
import { registerAndLogin } from '../../services/auth-api'

function RegisterPage({ onAuthChange, onChangePage }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    interest: '',
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
      const user = await registerAndLogin({
        name: formData.name,
        email: formData.email,
        password: formData.password,
      })
      onAuthChange(user)
      setStatus('success')
      setMessage('Conta criada com sucesso.')
      onChangePage('home')
    } catch (error) {
      setStatus('error')
      setMessage(
        error instanceof ApiError
          ? error.message
          : 'Nao foi possivel criar sua conta agora.',
      )
    }
  }

  return (
    <section className="account-page">
      <div className="page-lead">
        <p className="story-kicker">Cadastro</p>
        <h1>Crie sua conta para acompanhar noticias, salvar leituras e montar seu feed editorial.</h1>
        <p>
          O registro prepara o portal para favoritos, historico de leitura,
          alertas e uma experiencia personalizada dentro do Nexus IA.
        </p>
      </div>

      <div className="account-grid">
        <form className="account-card" onSubmit={handleSubmit}>
          <h2>Abrir conta</h2>
          <label>
            Nome completo
            <input
              type="text"
              placeholder="Seu nome"
              value={formData.name}
              onChange={handleChange('name')}
              required
            />
          </label>
          <label>
            Email
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
              placeholder="Crie uma senha"
              value={formData.password}
              onChange={handleChange('password')}
              minLength={6}
              required
            />
          </label>
          <label>
            Cargo ou interesse
            <input
              type="text"
              placeholder="Editor, leitor, pesquisador..."
              value={formData.interest}
              onChange={handleChange('interest')}
            />
          </label>
          {message ? (
            <p className={status === 'error' ? 'account-message is-error' : 'account-message is-success'}>
              {message}
            </p>
          ) : null}
          <button className="submit-button" type="submit">
            {status === 'loading' ? 'Criando conta...' : 'Criar conta Nexus IA'}
          </button>
        </form>

        <aside className="benefit-panel">
          <h2>O que voce libera com a conta</h2>
          <ul>
            <li>Salvar materias e montar leitura posterior</li>
            <li>Receber alertas por editoria</li>
            <li>Acompanhar newsletters e destaques da plataforma</li>
            <li>Entrar direto na area de leitura e preferencias</li>
          </ul>
          <button className="inline-button" type="button" onClick={() => onChangePage('login')}>
            Ja tem conta? Fazer login
          </button>
        </aside>
      </div>
    </section>
  )
}

export default RegisterPage
