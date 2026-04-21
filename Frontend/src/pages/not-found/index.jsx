function NotFoundPage({ onChangePage }) {
  return (
    <section className="editorial-placeholder">
      <p className="story-kicker">Pagina indisponivel</p>
      <h1>Essa pagina nao existe mais.</h1>
      <p>
        O link pode estar desatualizado ou a editoria pode ter sido removida do portal.
        Voce pode voltar para a capa e continuar a navegacao por uma das secoes ativas.
      </p>
      <div>
        <button className="primary-link" type="button" onClick={() => onChangePage('home')}>
          Voltar para a home
        </button>
      </div>
    </section>
  )
}

export default NotFoundPage
