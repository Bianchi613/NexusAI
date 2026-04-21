import EditorialPage from '../../components/editorial-page/index.jsx'

export default function NoticiasPage({ onChangePage, onOpenArticle }) {
  return <EditorialPage page="noticias" onChangePage={onChangePage} onOpenArticle={onOpenArticle} />
}
