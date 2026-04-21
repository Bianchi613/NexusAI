import EditorialPage from '../../components/editorial-page/index.jsx'

export default function VideosPage({ onChangePage, onOpenArticle }) {
  return <EditorialPage page="videos" onChangePage={onChangePage} onOpenArticle={onOpenArticle} />
}
