function NotFoundPage({
  onChangePage,
  kicker = 'Pagina indisponivel',
  title = 'Essa pagina nao existe mais.',
  description = (
    'O link pode estar desatualizado ou a editoria pode ter sido removida do portal. '
    + 'Voce pode voltar para a capa e continuar a navegacao por uma das secoes ativas.'
  ),
}) {
  return (
    <section className="editorial-placeholder">
      <p className="story-kicker">{kicker}</p>
      <h1>{title}</h1>
      <p>{description}</p>
      <div>
        <button className="primary-link" type="button" onClick={() => onChangePage('home')}>
          Voltar para a home
        </button>
      </div>
    </section>
  )
}

export default NotFoundPage
