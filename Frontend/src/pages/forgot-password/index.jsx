import { useState } from 'react'
import '../../styles/account-pages.css'
import { ApiError } from '../../services/portal-api'
import { requestPasswordReset } from '../../services/auth-api'

function ForgotPasswordPage({ onChangePage }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')
  const [helperMessage, setHelperMessage] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setStatus('loading')
    setMessage('')
    setHelperMessage('')

    try {
      const payload = await requestPasswordReset(email)
      setStatus('success')
      setMessage(payload.message || 'Solicitacao enviada com sucesso.')

      if (payload?.reset_token) {
        setHelperMessage(
          `Token gerado para este ambiente. Validade: ${payload.expires_in_minutes ?? 30} minutos.`,
        )
        onChangePage('reset-password')
        return
      }

      setHelperMessage('Se a conta existir, siga para a redefinicao quando tiver o token.')
    } catch (error) {
      setStatus('error')
      setMessage(
        error instanceof ApiError
          ? error.message
          : 'Nao foi possivel iniciar a recuperacao de senha.',
      )
    }
  }

  return (
    <section className="account-page">
      <div className="page-lead">
        <p className="story-kicker">Recuperacao</p>
        <h1>Recupere sua senha para voltar ao portal e continuar a navegacao.</h1>
        <p>
          Informe o e-mail da conta. Quando o envio estiver configurado, o portal manda um link
          de redefinicao por e-mail. Em ambiente local sem provedor, o token continua disponivel
          diretamente para teste.
        </p>
      </div>

      <div className="account-grid">
        <form className="account-card" onSubmit={handleSubmit}>
          <h2>Solicitar redefinicao</h2>
          <label>
            E-mail
            <input
              type="email"
              placeholder="voce@nexus.ai"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          {message ? (
            <p className={status === 'error' ? 'account-message is-error' : 'account-message is-success'}>
              {message}
            </p>
          ) : null}
          {helperMessage ? <p className="account-helper">{helperMessage}</p> : null}
          <button className="submit-button" type="submit">
            {status === 'loading' ? 'Gerando token...' : 'Enviar recuperacao'}
          </button>
          <button className="ghost-button" type="button" onClick={() => onChangePage('login')}>
            Voltar para login
          </button>
        </form>

        <aside className="benefit-panel">
          <h2>Como funciona agora</h2>
          <ul>
            <li>Voce informa o e-mail da conta</li>
            <li>O backend valida se existe usuario ativo</li>
            <li>Com Resend configurado, o link chega por e-mail</li>
            <li>Sem provedor, o token temporario segue disponivel para teste local</li>
          </ul>
          <button className="inline-button" type="button" onClick={() => onChangePage('reset-password')}>
            Ja tenho token
          </button>
        </aside>
      </div>
    </section>
  )
}

export default ForgotPasswordPage
