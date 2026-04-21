import { useState } from 'react'
import '../../styles/account-pages.css'
import { ApiError } from '../../services/portal-api'
import {
  getStoredPasswordResetToken,
  resetPasswordWithToken,
  storePasswordResetToken,
} from '../../services/auth-api'

function getTokenFromHash() {
  if (typeof window === 'undefined') {
    return ''
  }

  const rawHash = window.location.hash.replace(/^#/, '')
  const queryString = rawHash.includes('?') ? rawHash.split('?').slice(1).join('?') : ''

  if (!queryString) {
    return ''
  }

  return new URLSearchParams(queryString).get('token') ?? ''
}

function ResetPasswordPage({ onChangePage }) {
  const initialToken = getTokenFromHash() || getStoredPasswordResetToken() || ''
  const [formData, setFormData] = useState({
    token: initialToken,
    newPassword: '',
    confirmPassword: '',
  })
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')

  const handleChange = (field) => (event) => {
    const nextValue = event.target.value
    setFormData((current) => ({
      ...current,
      [field]: nextValue,
    }))

    if (field === 'token') {
      storePasswordResetToken(nextValue)
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus('loading')
    setMessage('')

    if (formData.newPassword !== formData.confirmPassword) {
      setStatus('error')
      setMessage('A confirmacao da senha precisa ser igual a nova senha.')
      return
    }

    try {
      const payload = await resetPasswordWithToken({
        token: formData.token.trim(),
        newPassword: formData.newPassword,
      })
      setStatus('success')
      setMessage(payload.message || 'Senha redefinida com sucesso.')
      onChangePage('login')
    } catch (error) {
      setStatus('error')
      setMessage(
        error instanceof ApiError
          ? error.message
          : 'Nao foi possivel redefinir a senha agora.',
      )
    }
  }

  return (
    <section className="account-page">
      <div className="page-lead">
        <p className="story-kicker">Nova senha</p>
        <h1>Defina uma nova senha para voltar a acessar o Nexus IA.</h1>
        <p>
          Use o token recebido ou abra o link enviado por e-mail. Se o token vier na URL,
          esta tela preenche o campo automaticamente para voce concluir a redefinicao.
        </p>
      </div>

      <div className="account-grid">
        <form className="account-card" onSubmit={handleSubmit}>
          <h2>Redefinir senha</h2>
          <label>
            Token
            <input
              type="text"
              placeholder="Cole o token recebido"
              value={formData.token}
              onChange={handleChange('token')}
              required
            />
          </label>
          <label>
            Nova senha
            <input
              type="password"
              placeholder="Digite a nova senha"
              value={formData.newPassword}
              onChange={handleChange('newPassword')}
              minLength={6}
              required
            />
          </label>
          <label>
            Confirmar nova senha
            <input
              type="password"
              placeholder="Repita a nova senha"
              value={formData.confirmPassword}
              onChange={handleChange('confirmPassword')}
              minLength={6}
              required
            />
          </label>
          {message ? (
            <p className={status === 'error' ? 'account-message is-error' : 'account-message is-success'}>
              {message}
            </p>
          ) : null}
          <button className="submit-button" type="submit">
            {status === 'loading' ? 'Salvando senha...' : 'Salvar nova senha'}
          </button>
          <button className="ghost-button" type="button" onClick={() => onChangePage('login')}>
            Voltar para login
          </button>
        </form>

        <aside className="benefit-panel">
          <h2>Boas praticas</h2>
          <ul>
            <li>Use uma senha diferente da anterior</li>
            <li>Prefira uma combinacao com letras, numeros e simbolos</li>
            <li>Conclua o processo antes do vencimento do token</li>
            <li>Depois da redefinicao, o login volta a funcionar normalmente</li>
          </ul>
          <button className="inline-button" type="button" onClick={() => onChangePage('forgot-password')}>
            Solicitar novo token
          </button>
        </aside>
      </div>
    </section>
  )
}

export default ResetPasswordPage
