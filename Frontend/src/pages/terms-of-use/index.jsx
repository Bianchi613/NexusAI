import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: 'Uso do portal',
    paragraphs: [
      'O Nexus IA e um portal editorial experimental voltado para leitura, navegacao por editorias e acompanhamento de materias publicadas a partir do backend do projeto.',
      'Ao continuar usando a plataforma, o leitor concorda em navegar de forma licita, sem tentar comprometer rotas, autenticacao, integracoes ou a experiencia de outros usuarios.',
    ],
  },
  {
    title: 'Conta e acesso',
    paragraphs: [
      'Algumas areas podem depender de cadastro e autenticacao. Cada usuario e responsavel pelas informacoes fornecidas no registro e pelo uso da propria sessao dentro da plataforma.',
      'O portal pode ajustar fluxos de login, cadastro e revisao editorial conforme a evolucao do produto, sempre preservando a coerencia com a proposta jornalistica da aplicacao.',
    ],
  },
  {
    title: 'Conteudo e operacao',
    paragraphs: [
      'As materias exibidas no Nexus IA dependem do pipeline de coleta, processamento, revisao e publicacao. Isso significa que o acervo pode mudar com frequencia conforme novas publicacoes entram no sistema.',
      'O projeto pode atualizar layout, navegacao, blocos editoriais e regras de exibicao sem aviso previo quando essas mudancas forem necessarias para a operacao do portal.',
    ],
  },
]

export default function TermsOfUsePage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Informacoes legais"
      title="Termos de uso"
      intro="Estas diretrizes explicam como o portal pode ser utilizado durante a navegacao, os testes e a leitura das materias publicadas no Nexus IA."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
