import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: 'Responsavel pelo projeto',
    paragraphs: [
      'Alan Bianchi e o criador do portal de noticias Nexus IA por inteligencia artificial.',
      'O projeto foi desenvolvido por ele como parte do Bacharelado em Sistema de Informacao, unindo fluxo editorial, integracao de dados e publicacao de materias em uma plataforma propria.',
    ],
  },
  {
    title: 'Contato direto',
    paragraphs: [
      'Para falar sobre o portal, arquitetura da plataforma, fluxo de geracao de noticias, integracoes ou apresentacao academica do projeto, o contato oficial e alanbianchi@coppe.ufrj.br.',
      'Este canal tambem pode ser usado para duvidas, sugestoes, colaboracoes e assuntos institucionais ligados ao Nexus IA.',
    ],
  },
  {
    title: 'Sobre o Nexus IA',
    paragraphs: [
      'O Nexus IA foi pensado como um portal de noticias apoiado por inteligencia artificial, com foco em organizacao editorial, leitura por categorias e renderizacao dinamica de materias publicadas.',
    ],
  },
]

export default function ContactPage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Canal institucional"
      title="Contato"
      intro="Alan Bianchi assina a criacao do Nexus IA como projeto do Bacharelado em Sistema de Informacao e concentra aqui o contato institucional do portal."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
