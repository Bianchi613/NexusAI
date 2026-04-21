import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: 'Dados de cadastro',
    paragraphs: [
      'Quando o leitor cria uma conta, o portal pode armazenar informacoes basicas de autenticacao e identificacao necessarias para acesso e continuidade da experiencia.',
      'Esses dados sao usados para manter sessao, identificar o perfil autenticado e sustentar os fluxos previstos pela aplicacao.',
    ],
  },
  {
    title: 'Uso operacional',
    paragraphs: [
      'Informacoes tecnicas, de navegacao e de uso podem ser tratadas para garantir funcionamento do frontend, integracao com o backend e estabilidade das rotas publicas e autenticadas.',
      'O objetivo principal do tratamento e manter o produto operando de forma consistente, com leitura, login e acesso editorial funcionando dentro do ambiente do portal.',
    ],
  },
  {
    title: 'Evolucao da politica',
    paragraphs: [
      'Como o Nexus IA ainda esta em evolucao, esta politica pode ser refinada para acompanhar novas funcionalidades, novas camadas de integracao e ajustes no fluxo editorial.',
      'Sempre que houver mudancas relevantes na forma como o portal lida com dados, a pagina podera ser atualizada para refletir o estado mais recente da plataforma.',
    ],
  },
]

export default function PrivacyPolicyPage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Informacoes legais"
      title="Politica de privacidade"
      intro="Esta pagina resume como o Nexus IA trata dados basicos de uso e autenticacao para manter o portal funcionando durante a navegacao."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
