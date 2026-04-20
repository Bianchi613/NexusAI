import '../../styles/account-pages.css'

function RegisterPage({ onChangePage }) {
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
        <form className="account-card" onSubmit={(event) => event.preventDefault()}>
          <h2>Abrir conta</h2>
          <label>
            Nome completo
            <input type="text" placeholder="Seu nome" />
          </label>
          <label>
            Email
            <input type="email" placeholder="voce@nexus.ai" />
          </label>
          <label>
            Senha
            <input type="password" placeholder="Crie uma senha" />
          </label>
          <label>
            Cargo ou interesse
            <input type="text" placeholder="Editor, leitor, pesquisador..." />
          </label>
          <button className="submit-button" type="submit">
            Criar conta Nexus IA
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
