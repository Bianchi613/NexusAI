import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: '1. Quais dados podemos coletar',
    paragraphs: [
      'Podemos coletar algumas informacoes quando voce usa o Nexus IA, como dados de navegacao, acesso e uso da plataforma.',
      'Tambem podem ser coletadas informacoes tecnicas do dispositivo, navegador, IP e conexao.',
      'Se voce preencher formularios, cadastro, contato ou newsletter, poderemos tratar os dados fornecidos nesses canais.',
      'Preferencias de conteudo, categorias, interesses de navegacao e interacoes com paginas, materias, recursos e comunicacoes do portal tambem podem ser consideradas no funcionamento da plataforma.',
    ],
  },
  {
    title: '2. Como coletamos esses dados',
    paragraphs: [
      'Os dados podem ser coletados diretamente por voce, quando preenche formularios, entra em contato ou se cadastra.',
      'Tambem podem ser coletados automaticamente, por meio de cookies, logs e tecnologias semelhantes.',
      'Quando aplicavel, a coleta tambem pode ocorrer por integracao com ferramentas e servicos de terceiros.',
    ],
  },
  {
    title: '3. Como usamos seus dados',
    paragraphs: [
      'Podemos usar suas informacoes para operar, manter e melhorar o Nexus IA.',
      'Esses dados tambem podem ser usados para personalizar sua experiencia e recomendar conteudos.',
      'O Nexus IA pode utilizar informacoes para medir desempenho, audiencia e uso da plataforma.',
      'Quando autorizado, poderemos enviar comunicacoes, newsletters ou avisos.',
      'As informacoes tambem podem ser usadas para proteger a seguranca da plataforma, prevenir fraudes, abusos ou usos indevidos e cumprir obrigacoes legais e regulatorias.',
    ],
  },
  {
    title: '4. Cookies e tecnologias semelhantes',
    paragraphs: [
      'O Nexus IA pode utilizar cookies e tecnologias parecidas para lembrar preferencias do usuario, entender como a plataforma e utilizada e melhorar desempenho, navegacao e conteudo.',
      'Esses recursos tambem podem apoiar metricas, estatisticas e personalizacao.',
      'Voce podera gerenciar cookies no navegador ou em eventuais configuracoes disponibilizadas pela plataforma.',
    ],
  },
  {
    title: '5. Compartilhamento de dados',
    paragraphs: [
      'Podemos compartilhar informacoes com prestadores de servico e fornecedores que apoiam a operacao do portal.',
      'Isso pode incluir ferramentas de hospedagem, analise, seguranca, envio de e-mails e infraestrutura.',
      'Tambem poderemos compartilhar dados com autoridades publicas ou orgaos competentes, quando houver obrigacao legal.',
      'Nao vendemos seus dados pessoais como pratica comum da plataforma.',
    ],
  },
  {
    title: '6. Conteudo de terceiros',
    paragraphs: [
      'O Nexus IA pode exibir links, embeds, feeds, APIs, conteudos agregados ou servicos de terceiros.',
      'Esses ambientes possuem politicas proprias de privacidade, e nao somos responsaveis pelas praticas adotadas por eles.',
    ],
  },
  {
    title: '7. Seguranca das informacoes',
    paragraphs: [
      'Adotamos medidas tecnicas e organizacionais razoaveis para proteger os dados sob nosso controle.',
      'Ainda assim, nenhum sistema e totalmente infalivel, e nao podemos garantir seguranca absoluta.',
    ],
  },
  {
    title: '8. Retencao dos dados',
    paragraphs: [
      'Manteremos os dados pelo tempo necessario para prestar os servicos da plataforma, cumprir finalidades legitimas de operacao e seguranca e atender obrigacoes legais, regulatorias ou contratuais.',
      'Quando possivel e adequado, os dados poderao ser excluidos, anonimizados ou armazenados de forma segura apos esse periodo.',
    ],
  },
  {
    title: '9. Seus direitos',
    paragraphs: [
      'Nos termos da legislacao aplicavel, especialmente a LGPD, voce podera solicitar, quando cabivel, confirmacao da existencia de tratamento de dados e acesso aos dados.',
      'Tambem podera solicitar correcao de dados incompletos, inexatos ou desatualizados, exclusao de dados quando aplicavel, informacao sobre compartilhamento de dados e revogacao do consentimento, quando o tratamento depender dele.',
    ],
  },
  {
    title: '10. Criancas e adolescentes',
    paragraphs: [
      'O Nexus IA nao e direcionado intencionalmente a criancas sem supervisao dos responsaveis.',
      'Caso seja identificado tratamento inadequado de dados de menores, poderemos adotar medidas para remover ou restringir essas informacoes.',
    ],
  },
  {
    title: '11. Alteracoes nesta politica',
    paragraphs: [
      'Esta Politica podera ser atualizada a qualquer momento para refletir mudancas legais, tecnicas ou operacionais.',
      'A versao mais recente sera sempre a publicada na plataforma.',
    ],
  },
  {
    title: '12. Contato',
    paragraphs: [
      'Se voce tiver duvidas sobre esta Politica de Privacidade ou quiser exercer seus direitos relacionados a dados pessoais, podera entrar em contato pelos canais oficiais informados no Nexus IA.',
    ],
  },
]

export default function PrivacyPolicyPage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Informacoes legais"
      title="Politica de privacidade"
      intro="Ultima atualizacao: 21 de abril de 2026. O Nexus IA valoriza a sua privacidade. Esta Politica explica, de forma simples, quais dados podemos coletar, como usamos essas informacoes e quais sao os seus direitos ao utilizar nossa plataforma. Ao acessar ou utilizar o Nexus IA, voce concorda com esta Politica de Privacidade."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
