import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: '1. Sobre o Nexus IA',
    paragraphs: [
      'O Nexus IA e um portal digital de noticias e conteudos informativos que pode utilizar sistemas automatizados, incluindo inteligencia artificial, para auxiliar na coleta, organizacao, categorizacao, resumo, geracao e publicacao de conteudos jornalisticos e informativos.',
      'Nestes Termos, "Nexus IA", "nos", "nosso" ou "plataforma" referem-se ao portal Nexus IA e seus responsaveis. "Usuario", "voce" ou "seu" referem-se a pessoa que acessa ou utiliza a plataforma.',
    ],
  },
  {
    title: '2. Aceitacao dos Termos',
    paragraphs: [
      'Ao acessar, navegar, cadastrar-se ou utilizar qualquer funcionalidade do Nexus IA, voce concorda com estes Termos de Uso e com a nossa Politica de Privacidade, quando aplicavel.',
      'Se voce nao concordar com estes Termos, nao devera utilizar a plataforma.',
    ],
  },
  {
    title: '3. Servicos oferecidos',
    paragraphs: [
      'O Nexus IA pode disponibilizar publicacao de noticias, reportagens, analises, resumos e conteudos informativos, bem como agregacao de informacoes oriundas de fontes publicas, feeds, APIs, parceiros ou outras origens autorizadas.',
      'A plataforma tambem pode oferecer categorizacao e organizacao de conteudos por temas, tags e assuntos, alem de funcionalidades de conta, favoritos, newsletter, comentarios ou outros recursos interativos, caso venham a existir.',
      'O uso de inteligencia artificial pode ocorrer como apoio editorial, sem prejuizo de revisao humana quando aplicavel.',
      'Podemos modificar, suspender, remover ou descontinuar qualquer funcionalidade, total ou parcialmente, a qualquer momento, com ou sem aviso previo.',
    ],
  },
  {
    title: '4. Uso permitido',
    paragraphs: [
      'Voce pode utilizar o Nexus IA para fins pessoais e informativos, de forma licita e em conformidade com estes Termos.',
      'Voce se compromete a nao utilizar a plataforma para violar leis, regulamentos ou direitos de terceiros, nem para copiar, raspar, minerar, automatizar ou extrair conteudos de forma nao autorizada.',
      'Tambem e proibido tentar invadir, testar vulnerabilidades, contornar protecoes tecnicas ou interferir no funcionamento da plataforma.',
      'Nao e permitido usar o conteudo do Nexus IA para treinar, alimentar, ajustar ou desenvolver modelos de inteligencia artificial sem autorizacao expressa.',
      'Voce tambem nao podera reproduzir a identidade visual, marca, nome, layout ou aparencia do Nexus IA de forma que gere confusao, nem utilizar a plataforma para divulgar conteudo ilicito, ofensivo, difamatorio, discriminatorio, enganoso ou que viole direitos de terceiros.',
    ],
  },
  {
    title: '5. Conteudo da plataforma',
    paragraphs: [
      'O conteudo disponibilizado no Nexus IA pode incluir textos, imagens, videos, audios, resumos, classificacoes, titulos, tags, materias geradas com auxilio de IA, elementos graficos, marca, logotipo, interface e demais materiais publicados na plataforma.',
      'Salvo indicacao em contrario, esses conteudos sao protegidos por direitos autorais, propriedade intelectual e demais normas aplicaveis.',
      'O uso do conteudo do Nexus IA nao transfere a voce qualquer direito de propriedade sobre ele.',
    ],
  },
  {
    title: '6. Uso de inteligencia artificial',
    paragraphs: [
      'O Nexus IA pode utilizar inteligencia artificial para apoiar processos editoriais, como consolidacao de fontes, sugestao de titulos, categorizacao, resumo e geracao de textos.',
      'Embora busquemos qualidade, coerencia e precisao, conteudos produzidos ou apoiados por IA podem conter limitacoes, imprecisoes, omissoes ou interpretacoes incorretas.',
      'Por isso, o usuario reconhece que nem todo conteudo e produzido exclusivamente por humanos, que os conteudos podem ser revisados, corrigidos, atualizados ou removidos a qualquer tempo, e que o Nexus IA nao garante que todo conteudo esteja sempre completo, atualizado ou livre de erros.',
    ],
  },
  {
    title: '7. Fontes de terceiros e links externos',
    paragraphs: [
      'O Nexus IA pode citar, agregar, referenciar ou direcionar o usuario para conteudos, sites, APIs, plataformas, redes sociais e servicos de terceiros.',
      'Nao somos responsaveis pelo conteudo, politicas, disponibilidade, seguranca ou praticas de servicos de terceiros. O acesso a esses servicos e de responsabilidade do proprio usuario, sujeito tambem aos termos e politicas dos respectivos provedores.',
    ],
  },
  {
    title: '8. Conta do usuario',
    paragraphs: [
      'Caso o Nexus IA ofereca cadastro, o usuario sera responsavel por fornecer informacoes verdadeiras, completas e atualizadas, manter a confidencialidade de sua senha e credenciais, e responder por toda atividade realizada em sua conta.',
      'Podemos suspender, restringir ou encerrar contas que violem estes Termos, a legislacao aplicavel ou a seguranca da plataforma.',
    ],
  },
  {
    title: '9. Conteudo enviado pelo usuario',
    paragraphs: [
      'Se o Nexus IA permitir comentarios, envio de mensagens, sugestoes, arquivos ou qualquer outro conteudo por usuarios, voce declara que possui os direitos necessarios sobre o que enviar.',
      'Voce nao podera enviar conteudo ilegal, ofensivo, abusivo, difamatorio ou discriminatorio, nem material que viole direitos autorais, marca, imagem, privacidade ou qualquer outro direito de terceiros.',
      'Tambem e vedado enviar virus, malware, scripts maliciosos, spam, fraude, publicidade nao autorizada ou tentativa de manipulacao.',
      'Ao enviar conteudo para a plataforma, voce autoriza o Nexus IA, de forma nao exclusiva e gratuita, a armazenar, exibir, reproduzir, adaptar e utilizar esse conteudo na medida necessaria para operacao, divulgacao e melhoria do servico, respeitados os limites legais aplicaveis.',
    ],
  },
  {
    title: '10. Remocao e moderacao',
    paragraphs: [
      'O Nexus IA podera, a seu exclusivo criterio, monitorar, revisar, restringir, editar ou remover conteudos, contas, comentarios, interacoes ou acessos que considere incompativeis com estes Termos, com a lei ou com a finalidade da plataforma.',
      'Essa faculdade nao cria obrigacao permanente de monitoramento previo.',
    ],
  },
  {
    title: '11. Propriedade intelectual',
    paragraphs: [
      'Todos os direitos relativos ao Nexus IA, incluindo sua marca, nome, logotipo, identidade visual, software, banco de dados, organizacao editorial e conteudo original, pertencem aos seus titulares.',
      'E proibido reproduzir, distribuir, modificar, republicar, comercializar ou explorar economicamente qualquer parte da plataforma sem autorizacao previa e expressa, salvo nos casos permitidos por lei.',
    ],
  },
  {
    title: '12. Compartilhamento',
    paragraphs: [
      'O usuario pode compartilhar links para materias e paginas do Nexus IA, desde que nao altere a autoria ou o contexto do conteudo, nao faca parecer que existe endosso, parceria ou vinculo oficial inexistente, e nao utilize o conteudo de forma enganosa, ofensiva ou comercial nao autorizada.',
    ],
  },
  {
    title: '13. Isencoes de responsabilidade',
    paragraphs: [
      'O Nexus IA disponibiliza seus servicos e conteudos no estado em que se encontram e conforme disponibilidade.',
      'Nao garantimos que a plataforma funcionara sem interrupcoes ou erros, que o conteudo estara sempre completo, preciso ou atualizado, que a plataforma estara livre de falhas, virus ou indisponibilidades, ou que conteudos gerados, resumidos ou classificados por IA estarao sempre corretos.',
      'As informacoes do Nexus IA tem carater informativo e nao substituem aconselhamento profissional, juridico, medico, financeiro, tecnico ou de qualquer outra natureza especializada.',
    ],
  },
  {
    title: '14. Limitacao de responsabilidade',
    paragraphs: [
      'Na maxima extensao permitida pela legislacao aplicavel, o Nexus IA nao sera responsavel por danos indiretos, lucros cessantes, perda de dados, perda de oportunidade, danos reputacionais ou prejuizos decorrentes do uso ou da impossibilidade de uso da plataforma.',
      'Essa limitacao tambem abrange a confianca depositada em conteudo publicado, falhas tecnicas, indisponibilidades ou erros de terceiros, conteudo de terceiros, inclusive fontes externas e links, e informacoes geradas ou auxiliadas por sistemas de inteligencia artificial.',
      'Nada nestes Termos exclui responsabilidade que, por lei, nao possa ser excluida.',
    ],
  },
  {
    title: '15. Privacidade e dados pessoais',
    paragraphs: [
      'O tratamento de dados pessoais realizado pelo Nexus IA seguira a legislacao aplicavel e a respectiva Politica de Privacidade, quando disponivel.',
      'Ao utilizar a plataforma, voce reconhece que determinados dados tecnicos e de navegacao podem ser coletados para fins de funcionamento, seguranca, metricas, personalizacao e melhoria dos servicos.',
    ],
  },
  {
    title: '16. Alteracoes destes Termos',
    paragraphs: [
      'Podemos alterar estes Termos de Uso a qualquer momento. A versao atualizada passara a valer a partir de sua publicacao na plataforma.',
      'Recomendamos que voce consulte este documento periodicamente. O uso continuado do Nexus IA apos a publicacao de alteracoes sera considerado como aceitacao da nova versao.',
    ],
  },
  {
    title: '17. Suspensao e encerramento',
    paragraphs: [
      'Podemos suspender ou encerrar o acesso do usuario ao Nexus IA, total ou parcialmente, a qualquer momento, especialmente em caso de violacao destes Termos, uso indevido da plataforma, risco a seguranca, integridade ou funcionamento do servico, ou exigencia legal ou regulatoria.',
    ],
  },
  {
    title: '18. Legislacao aplicavel e foro',
    paragraphs: [
      'Estes Termos serao regidos pelas leis da Republica Federativa do Brasil.',
      'Fica eleito o foro da comarca do domicilio do responsavel pela plataforma ou, quando exigido por lei, o foro aplicavel ao consumidor, para dirimir quaisquer controversias relacionadas ao Nexus IA.',
    ],
  },
]

export default function TermsOfUsePage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Informacoes legais"
      title="Termos de uso"
      intro="Ultima atualizacao: 21 de abril de 2026. Estes Termos de Uso regulam o acesso e a utilizacao do Nexus IA, de seus conteudos, funcionalidades e servicos. Ao acessar ou utilizar o portal, voce declara que leu, entendeu e concorda com estas regras."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
