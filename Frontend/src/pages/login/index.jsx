import '../../styles/account-pages.css'

function LoginPage({ onChangePage }) {
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
        <form className="account-card" onSubmit={(event) => event.preventDefault()}>
          <h2>Acessar conta</h2>
          <label>
            E-mail
            <input type="email" placeholder="voce@nexus.ai" />
          </label>
          <label>
            Senha
            <input type="password" placeholder="Sua senha" />
          </label>
          <button className="submit-button" type="submit">
            Entrar
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
