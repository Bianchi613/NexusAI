export const categoryPageContent = {
  noticias: {
    eyebrow: 'Noticias',
    title: 'Noticias',
    description:
      'A editoria principal concentra desdobramentos, atualizacoes e contexto para acompanhar o ritmo continuo da cobertura.',
    railTitle: 'Frentes da editoria',
    railItems: [
      'Breaking news e desdobramentos ao longo do dia',
      'Chamadas de contexto para leitura rapida',
      'Blocos de continuidade para assuntos em andamento',
    ],
  },
  negocios: {
    eyebrow: 'Negocios',
    title: 'Negocios',
    description:
      'Empresas, mercado e impacto economico aparecem aqui com recorte editorial, leitura guiada e espaco para analise.',
    railTitle: 'Pontos de acompanhamento',
    railItems: [
      'Resultados, aquisicoes e movimentos corporativos',
      'Mercado, investimento e operacao de produto',
      'Sinais economicos que afetam empresas e setores',
    ],
  },
  tecnologia: {
    eyebrow: 'Tecnologia',
    title: 'Tecnologia',
    description:
      'Software, plataformas, IA e infraestrutura se organizam em uma pagina fixa pronta para cobertura recorrente.',
    railTitle: 'Assuntos em foco',
    railItems: [
      'Inteligencia artificial, plataformas e servicos digitais',
      'Infraestrutura, software e seguranca',
      'Produto, engenharia e lancamentos',
    ],
  },
  saude: {
    eyebrow: 'Saude',
    title: 'Saude',
    description:
      'A editoria de saude combina servico, contexto e acompanhamento de pesquisas, hospitais e politicas publicas.',
    railTitle: 'Guias da cobertura',
    railItems: [
      'Saude publica, hospitais e politica sanitaria',
      'Tratamentos, estudos e acompanhamento clinico',
      'Leitura de servico para o publico geral',
    ],
  },
  clima: {
    eyebrow: 'Clima',
    title: 'Clima',
    description:
      'Previsoes, alertas e eventos extremos entram em uma estrutura pronta para atualizacao constante e leitura pratica.',
    railTitle: 'Entradas da pagina',
    railItems: [
      'Alerta de chuva, calor e mudanca brusca de tempo',
      'Cobertura de impacto urbano e regional',
      'Contexto para semana, tendencia e risco',
    ],
  },
  cultura: {
    eyebrow: 'Cultura',
    title: 'Cultura',
    description:
      'Cinema, musica, livros e series aparecem com espaco para agenda, critica, lancamentos e desdobramentos.',
    railTitle: 'Recortes editoriais',
    railItems: [
      'Estreias, festivais e agenda cultural',
      'Critica, bastidores e entrevistas',
      'Series, musica, cinema e literatura',
    ],
  },
  politica: {
    eyebrow: 'Politica',
    title: 'Politica',
    description:
      'Agenda institucional, bastidores e impacto regulatorio sao organizados com hierarquia e continuidade de leitura.',
    railTitle: 'Linhas da cobertura',
    railItems: [
      'Executivo, legislativo e judiciario',
      'Votacoes, articulacao e agenda oficial',
      'Contexto para medidas e impacto institucional',
    ],
  },
  ciencia: {
    eyebrow: 'Ciencia',
    title: 'Ciencia',
    description:
      'Pesquisas, descobertas e inovacoes ganham uma pagina fixa com espaco para explicacao e aprofundamento.',
    railTitle: 'Pistas de leitura',
    railItems: [
      'Estudos academicos e descoberta cientifica',
      'Universidades, laboratorios e missao espacial',
      'Explicadores com contexto e aplicacao pratica',
    ],
  },
  videos: {
    eyebrow: 'Videos',
    title: 'Videos',
    description:
      'Clipes, entrevistas e trechos especiais ficam em uma editoria pensada para destaque visual e serie recorrente.',
    railTitle: 'Formatos da editoria',
    railItems: [
      'Entrevistas, bastidores e programas especiais',
      'Cortes de cobertura e clipes curtos',
      'Series em episodios e faixas de reproducao',
    ],
  },
}

export const articleRecords = [
  {
    slug: 'redacao-reorganiza-cobertura-em-blocos-de-plantao',
    page: 'noticias',
    category: 'Noticias',
    label: 'Plantao',
    title: 'Redacao reorganiza cobertura em blocos de plantao para acelerar atualizacoes da capa',
    summary:
      'A operacao editorial passou a distribuir noticias em janelas de acompanhamento continuo para reduzir retrabalho na home.',
    excerpt:
      'A nova grade prioriza entradas curtas, contexto e desdobramentos publicados em ciclos ao longo do dia.',
    author: 'Redacao Nexus IA',
    publishedAt: '20 abr 2026, 08h15',
    readTime: '4 min',
    location: 'Sao Paulo',
    tags: ['plantao', 'redacao', 'home'],
    body: [
      'A equipe editorial do Nexus IA reorganizou a cobertura em blocos de plantao para manter a capa atualizada sem quebrar a hierarquia da pagina principal. A mudanca concentra o trabalho em janelas de acompanhamento e define pontos de revisao antes da publicacao final.',
      'Com o novo formato, cada assunto principal recebe uma entrada inicial, seguida por atualizacoes curtas quando ha novos desdobramentos. O objetivo e manter a leitura fluida para quem chega pela home e, ao mesmo tempo, abrir espaco para contextualizacao nas editorias.',
      'Segundo o time do portal, a estrutura tambem facilita a distribuicao das noticias por categoria, permitindo que as paginas fixas de editoria reflitam o mesmo ritmo de publicacao adotado na capa.',
    ],
  },
  {
    slug: 'painel-de-alertas-passa-a-indicar-prioridade-por-assunto',
    page: 'noticias',
    category: 'Noticias',
    label: 'Operacao',
    title: 'Painel de alertas passa a indicar prioridade por assunto e etapa de apuracao',
    summary:
      'O fluxo de triagem ganhou marcadores para diferenciar pauta urgente, acompanhamento e contexto antes da publicacao.',
    excerpt:
      'A classificacao por prioridade ajuda a decidir o que entra primeiro na capa e o que segue para aprofundamento.',
    author: 'Equipe de Produto Editorial',
    publishedAt: '20 abr 2026, 09h40',
    readTime: '3 min',
    location: 'Sao Paulo',
    tags: ['alertas', 'triagem', 'apuracao'],
    body: [
      'O painel interno de alertas do portal passou a sinalizar o nivel de prioridade de cada assunto e a etapa de apuracao em que ele se encontra. A equipe pode distinguir com mais clareza o que exige entrada imediata do que ainda depende de consolidacao.',
      'A classificacao foi desenhada para reduzir duplicidade de cobertura e para orientar o encaminhamento das pautas entre a home e as editorias. Assuntos urgentes seguem para destaque rapido, enquanto materias com base suficiente podem entrar em formato mais analitico.',
      'A mudanca serve como base para o modelo de paginas fixas por categoria, que passam a receber artigos com contexto ja filtrado pelo fluxo de triagem.',
    ],
  },
  {
    slug: 'capa-ganha-blocos-de-contexto-para-desdobramentos-longos',
    page: 'noticias',
    category: 'Noticias',
    label: 'Contexto',
    title: 'Capa ganha blocos de contexto para acompanhar assuntos com desdobramento longo',
    summary:
      'O portal adotou modulos secundarios para recuperar antecedentes e pontos-chave sem interromper a leitura da noticia principal.',
    excerpt:
      'Os blocos passam a funcionar como apoio para coberturas que exigem cronologia e contextualizacao constante.',
    author: 'Nucleo de Conteudo',
    publishedAt: '20 abr 2026, 11h05',
    readTime: '5 min',
    location: 'Sao Paulo',
    tags: ['contexto', 'cronologia', 'cobertura'],
    body: [
      'A home do Nexus IA passou a incluir blocos de contexto para assuntos que se estendem por varios dias e dependem de acompanhamento cronologico. A proposta e resumir antecedentes sem deslocar o leitor para fora da narrativa principal.',
      'Cada modulo traz pontos-chave, situacao atual e referencia para os proximos movimentos da cobertura. O formato foi pensado para funcionar tanto na capa quanto dentro das paginas fixas de categoria.',
      'A equipe considera que a mudanca melhora a retencao de leitura em temas complexos e facilita a atualizacao editorial quando surgem novos fatos relacionados ao mesmo assunto.',
    ],
  },
  {
    slug: 'painel-de-receita-das-editorias-orienta-prioridade-comercial',
    page: 'negocios',
    category: 'Negocios',
    label: 'Mercado',
    title: 'Painel de receita das editorias passa a orientar a prioridade comercial do portal',
    summary:
      'O acompanhamento de assinaturas, publicidade e permanencia de leitura passou a influenciar a ordem de destaque de alguns blocos.',
    excerpt:
      'A leitura de negocios agora observa desempenho de produto e impacto economico dentro da operacao editorial.',
    author: 'Mesa de Negocios',
    publishedAt: '20 abr 2026, 08h55',
    readTime: '4 min',
    location: 'Rio de Janeiro',
    tags: ['receita', 'assinaturas', 'mercado'],
    body: [
      'O portal implantou um painel que acompanha sinais de receita por editoria para orientar discussoes sobre prioridade comercial e estrategia de distribuicao. O monitoramento considera assinaturas, publicidade e tempo de permanencia nas paginas.',
      'A leitura desses indicadores nao substitui o criterio editorial, mas ajuda a identificar quais blocos de cobertura podem receber mais destaque em ciclos especificos. O foco atual esta em equilibrar interesse do publico e impacto economico.',
      'Na editoria de negocios, a mudanca se traduz em mais espaco para temas ligados a monetizacao, mercado e desempenho das frentes do produto.',
    ],
  },
  {
    slug: 'empresas-do-ecossistema-de-ia-ganham-trilha-propria-no-portal',
    page: 'negocios',
    category: 'Negocios',
    label: 'Empresas',
    title: 'Empresas do ecossistema de IA ganham trilha propria de acompanhamento no portal',
    summary:
      'A cobertura de negocios passou a separar movimentacoes corporativas ligadas a IA, software e infraestrutura.',
    excerpt:
      'O recorte busca dar continuidade a aportes, parcerias, aquisicoes e reorganizacoes do setor.',
    author: 'Redacao de Negocios',
    publishedAt: '20 abr 2026, 10h20',
    readTime: '4 min',
    location: 'Sao Paulo',
    tags: ['empresas', 'ia', 'investimento'],
    body: [
      'A editoria de negocios abriu uma trilha especifica para empresas ligadas ao ecossistema de inteligencia artificial, software e infraestrutura digital. O objetivo e manter historico de movimentos corporativos que costumam evoluir em etapas.',
      'Nesse acompanhamento entram anuncios de parceria, aporte, compra de empresa, reorganizacao interna e expansao de produto. O formato permite retomar rapidamente o contexto cada vez que ha um novo desdobramento.',
      'A iniciativa tambem conversa com a cobertura de tecnologia, mas a prioridade desta pagina e destacar impacto economico, estrategia de mercado e efeito sobre concorrencia.',
    ],
  },
  {
    slug: 'indicadores-de-leitura-passam-a-entrar-nos-relatorios-de-produto',
    page: 'negocios',
    category: 'Negocios',
    label: 'Produto',
    title: 'Indicadores de leitura passam a entrar nos relatorios de produto e operacao comercial',
    summary:
      'Dados de consumo das materias agora ajudam a orientar oferta editorial e discussoes sobre recorrencia de publico.',
    excerpt:
      'A combinacao de audiencia e recorrencia passou a influenciar debates sobre crescimento do portal.',
    author: 'Equipe de Estrategia',
    publishedAt: '20 abr 2026, 12h10',
    readTime: '3 min',
    location: 'Belo Horizonte',
    tags: ['produto', 'audiencia', 'dados'],
    body: [
      'Os relatorios internos de produto passaram a incluir indicadores de leitura das materias para apoiar discussoes sobre crescimento e recorrencia de publico. A integracao aproxima dados editoriais e metas de negocio.',
      'Com esse acompanhamento, o portal consegue observar quais temas sustentam retorno frequente do leitor e quais tipos de chamada geram abertura de conta ou aprofundamento de navegacao.',
      'A leitura consolidada desses dados deve orientar futuras decisoes sobre assinatura, newsletters e novos formatos dentro da cobertura de negocios.',
    ],
  },
  {
    slug: 'camada-de-busca-interna-reordena-resultados-por-contexto',
    page: 'tecnologia',
    category: 'Tecnologia',
    label: 'Produto',
    title: 'Camada de busca interna reordena resultados por contexto e tempo de publicacao',
    summary:
      'O sistema passou a combinar recencia com relevancia editorial para exibir materias relacionadas nas paginas do portal.',
    excerpt:
      'A mudanca foi desenhada para evitar listas repetitivas e recuperar textos de contexto quando o assunto volta ao noticiario.',
    author: 'Desk de Tecnologia',
    publishedAt: '20 abr 2026, 07h50',
    readTime: '4 min',
    location: 'Campinas',
    tags: ['busca', 'software', 'produto'],
    body: [
      'A camada de busca interna do portal passou a combinar tempo de publicacao com relevancia editorial na hora de montar resultados relacionados. A alteracao tenta reduzir repeticiones e melhorar a recuperacao de materiais de contexto.',
      'Na pratica, a busca deixa de privilegiar apenas o texto mais recente e passa a considerar se aquela materia ajuda a explicar o assunto principal. Isso e especialmente importante em coberturas com muitos desdobramentos tecnicos.',
      'O recurso deve ser usado nas paginas de artigo para sugerir leituras complementares sem depender apenas de listas manuais.',
    ],
  },
  {
    slug: 'painel-de-observabilidade-passa-a-monitorar-falhas-de-publicacao',
    page: 'tecnologia',
    category: 'Tecnologia',
    label: 'Infraestrutura',
    title: 'Painel de observabilidade passa a monitorar falhas de publicacao em tempo real',
    summary:
      'A equipe tecnica centralizou alertas de indisponibilidade e atraso de processamento em um unico painel de acompanhamento.',
    excerpt:
      'A iniciativa busca diminuir o tempo entre a identificacao de erro e a correcao no fluxo de publicacao.',
    author: 'Infra Nexus IA',
    publishedAt: '20 abr 2026, 09h05',
    readTime: '5 min',
    location: 'Curitiba',
    tags: ['infraestrutura', 'observabilidade', 'publicacao'],
    body: [
      'O time tecnico do Nexus IA centralizou alertas de falha em um painel de observabilidade para acompanhar indisponibilidade, atraso de processamento e erro de entrega no fluxo de publicacao. A meta e encurtar o tempo de resposta.',
      'O painel tambem registra comportamento fora do padrao em componentes que abastecem home, editorias e pagina de artigo. Assim, a equipe consegue localizar de forma mais rapida em qual etapa do pipeline o problema surgiu.',
      'Segundo a operacao, a ferramenta sera decisiva quando o portal passar a renderizar materias diretamente a partir do banco de dados.',
    ],
  },
  {
    slug: 'modelo-de-tags-fica-mais-estrito-para-reduzir-ruido',
    page: 'tecnologia',
    category: 'Tecnologia',
    label: 'Dados',
    title: 'Modelo de tags fica mais estrito para reduzir ruido na classificacao das materias',
    summary:
      'A camada tecnica revisou regras de normalizacao para evitar variacoes desnecessarias na taxonomia editorial.',
    excerpt:
      'A unificacao das tags deve melhorar busca, recomendacao e leitura por categoria.',
    author: 'Equipe de Plataforma',
    publishedAt: '20 abr 2026, 11h35',
    readTime: '3 min',
    location: 'Recife',
    tags: ['tags', 'taxonomia', 'dados'],
    body: [
      'A plataforma editorial revisou as regras de tags para reduzir ruido na classificacao das materias e melhorar o aproveitamento da taxonomia em busca e recomendacao. O objetivo e evitar variacoes pequenas para o mesmo tema.',
      'Com a normalizacao, diferentes formas de um mesmo assunto passam a ser consolidadas em etiquetas unicas, o que facilita a navegacao por categoria e melhora a distribuicao de leituras relacionadas.',
      'A equipe afirma que o ajuste tambem prepara o portal para renderizacao dinamica de artigos, uma vez que a consistencia dos metadados passa a ter peso maior no resultado exibido ao leitor.',
    ],
  },
  {
    slug: 'rede-de-hospitais-testa-painel-unificado-de-atendimento',
    page: 'saude',
    category: 'Saude',
    label: 'Hospitais',
    title: 'Rede de hospitais testa painel unificado para acompanhar fila e ocupacao em tempo real',
    summary:
      'A ferramenta reune sinais operacionais para facilitar resposta a picos de atendimento e reorganizacao de equipes.',
    excerpt:
      'O acompanhamento de ocupacao, triagem e disponibilidade virou base para novas rotinas de monitoramento.',
    author: 'Editoria de Saude',
    publishedAt: '20 abr 2026, 08h05',
    readTime: '4 min',
    location: 'Porto Alegre',
    tags: ['hospitais', 'atendimento', 'monitoramento'],
    body: [
      'Uma rede de hospitais iniciou testes com um painel unificado para acompanhar fila de atendimento, ocupacao e distribuicao de equipes em tempo real. A proposta e reagir com mais rapidez a momentos de maior demanda.',
      'O sistema consolida sinais operacionais em uma unica tela e permite que gestores acompanhem gargalos de triagem e disponibilidade de leitos sem depender de consultas dispersas.',
      'Para a editoria de saude, o caso serve como exemplo de como indicadores clinicos e de operacao podem ser transformados em cobertura de servico e contexto para o leitor.',
    ],
  },
  {
    slug: 'guia-de-cobertura-sobre-vacinas-ganha-area-fixa-no-portal',
    page: 'saude',
    category: 'Saude',
    label: 'Servico',
    title: 'Guia de cobertura sobre vacinas ganha area fixa para perguntas recorrentes e atualizacoes',
    summary:
      'A pagina foi desenhada para reunir informacoes recorrentes em um bloco permanente de servico ao leitor.',
    excerpt:
      'A estrutura resume duvidas frequentes e abre espaco para novas entradas sempre que houver atualizacao relevante.',
    author: 'Nucleo de Saude Publica',
    publishedAt: '20 abr 2026, 10h00',
    readTime: '4 min',
    location: 'Brasilia',
    tags: ['vacinas', 'guia', 'servico'],
    body: [
      'O portal criou uma area fixa para cobertura sobre vacinas com foco em perguntas recorrentes, servico e atualizacoes de contexto. A medida busca dar continuidade a um tema que costuma voltar ao noticiario em etapas.',
      'O guia concentra duvidas frequentes e orienta o leitor sobre como acompanhar novas informacoes quando a politica de imunizacao recebe ajustes ou comunicados oficiais.',
      'A pagina tambem funciona como referencia para futuras materias, que podem apontar para um mesmo nucleo de contexto em vez de repetir explicacoes basicas a cada novo texto.',
    ],
  },
  {
    slug: 'estudo-clinico-amplia-monitoramento-de-efeitos-adversos',
    page: 'saude',
    category: 'Saude',
    label: 'Pesquisa',
    title: 'Estudo clinico amplia monitoramento de efeitos adversos em acompanhamento de longo prazo',
    summary:
      'Pesquisadores passaram a observar por mais tempo a resposta de participantes para medir persistencia e seguranca.',
    excerpt:
      'O desenho do estudo reforca a importancia de acompanhar resultados para alem da fase inicial.',
    author: 'Equipe de Ciencia e Saude',
    publishedAt: '20 abr 2026, 13h10',
    readTime: '5 min',
    location: 'Ribeirao Preto',
    tags: ['estudo clinico', 'pesquisa', 'monitoramento'],
    body: [
      'Pesquisadores ampliaram o monitoramento de efeitos adversos em um estudo clinico de longo prazo para observar com mais precisao a persistencia das respostas entre os participantes. A extensao foi anunciada como parte do protocolo de acompanhamento.',
      'A equipe informou que o objetivo e reunir dados adicionais sobre seguranca e comportamento do tratamento ao longo do tempo, sem se limitar apenas aos resultados iniciais.',
      'Para a editoria de saude, o tema reforca a importancia de contextualizar pesquisa clinica e mostrar ao leitor em que etapa de validacao um resultado se encontra.',
    ],
  },
  {
    slug: 'mapa-de-chuva-intensa-passa-a-abrir-alertas-por-bairro',
    page: 'clima',
    category: 'Clima',
    label: 'Alerta',
    title: 'Mapa de chuva intensa passa a abrir alertas por bairro em atualizacao continua',
    summary:
      'A nova camada de cobertura meteorologica divide o risco em areas menores para facilitar leitura de impacto local.',
    excerpt:
      'A atualizacao por bairro ajuda a transformar previsao em servico mais direto para o leitor.',
    author: 'Desk de Clima',
    publishedAt: '20 abr 2026, 07h35',
    readTime: '4 min',
    location: 'Sao Paulo',
    tags: ['chuva', 'alerta', 'bairro'],
    body: [
      'O portal passou a destacar alertas de chuva intensa por bairro para tornar a cobertura meteorologica mais precisa e util em momentos de risco elevado. A mudanca organiza o acompanhamento em recortes menores dentro das grandes cidades.',
      'Em vez de um aviso unico para toda a regiao, a leitura passa a indicar onde ha maior probabilidade de acumulado e em quais faixas de horario o alerta ganha intensidade.',
      'A estrutura deve servir como base para futuras paginas de servico, em que dados do banco alimentarao automaticamente a area de clima com avisos segmentados.',
    ],
  },
  {
    slug: 'onda-de-calor-ganha-painel-com-tendencia-de-cinco-dias',
    page: 'clima',
    category: 'Clima',
    label: 'Previsao',
    title: 'Onda de calor ganha painel com tendencia de cinco dias e orientacoes de acompanhamento',
    summary:
      'A editoria passou a reunir previsao, contexto e servico em um bloco fixo para periodos de temperatura elevada.',
    excerpt:
      'O objetivo e reduzir dispersao das informacoes quando o mesmo evento se prolonga por varios dias.',
    author: 'Nucleo de Servico',
    publishedAt: '20 abr 2026, 10h45',
    readTime: '3 min',
    location: 'Goiania',
    tags: ['calor', 'previsao', 'tendencia'],
    body: [
      'A cobertura de clima ganhou um painel dedicado a ondas de calor com tendencia de cinco dias, pontos de atencao e orientacoes de acompanhamento. O bloco foi desenhado para concentrar informacoes que costumam ficar espalhadas em diferentes materias.',
      'A ideia e oferecer ao leitor uma leitura continua do episodio, com atualizacao conforme a previsao muda e sem necessidade de reconstruir o contexto a cada novo texto.',
      'No modelo futuro do portal, essa area devera ser alimentada por dados integrados e exibida de forma automatica na pagina da editoria.',
    ],
  },
  {
    slug: 'frente-fria-reorganiza-cobertura-regional-do-portal',
    page: 'clima',
    category: 'Clima',
    label: 'Regioes',
    title: 'Frente fria reorganiza cobertura regional do portal com entradas por impacto',
    summary:
      'A pagina passa a ordenar chamadas conforme alteracao de temperatura, chuva e efeito na rotina urbana.',
    excerpt:
      'O recorte por impacto ajuda a separar previsao tecnica de informacao pratica para o publico.',
    author: 'Equipe de Clima',
    publishedAt: '20 abr 2026, 12h25',
    readTime: '4 min',
    location: 'Curitiba',
    tags: ['frente fria', 'regioes', 'impacto'],
    body: [
      'A chegada de uma frente fria levou o portal a reorganizar a cobertura regional de clima em entradas separadas por tipo de impacto. Em vez de uma unica manchete, a pagina passa a dividir efeitos sobre temperatura, chuva e rotina urbana.',
      'O modelo ajuda a distinguir a informacao tecnica da previsao do servico mais pratico para o leitor, como deslocamento, risco de transtorno e janela de maior mudanca no tempo.',
      'A editoria considera esse formato importante para futuras integracoes com banco de dados, quando alertas e boletins poderao ocupar automaticamente posicoes especificas na pagina.',
    ],
  },
  {
    slug: 'festival-digital-reorganiza-estreias-em-janelas-tematicas',
    page: 'cultura',
    category: 'Cultura',
    label: 'Agenda',
    title: 'Festival digital reorganiza estreias em janelas tematicas para facilitar acompanhamento',
    summary:
      'A cobertura cultural passou a reunir lancamentos em blocos de programacao por tema e horario.',
    excerpt:
      'O formato ajuda o leitor a navegar por filmes, musica e encontros sem perder a sequencia do evento.',
    author: 'Editoria de Cultura',
    publishedAt: '20 abr 2026, 09h10',
    readTime: '4 min',
    location: 'Rio de Janeiro',
    tags: ['festival', 'agenda', 'estreias'],
    body: [
      'A editoria de cultura passou a organizar a cobertura de um festival digital em janelas tematicas para facilitar o acompanhamento da programacao. O leitor consegue localizar com mais rapidez as estreias e os encontros de cada faixa do evento.',
      'O formato substitui uma listagem linear por blocos separados por assunto, como cinema, musica e conversas com convidados. A mudanca foi pensada para tornar a leitura mais clara em coberturas de varios dias.',
      'A pagina fixa da editoria deve adotar esse mesmo principio quando passar a receber dados de agenda direto do banco.',
    ],
  },
  {
    slug: 'series-em-destaque-ganham-ficha-unica-de-acompanhamento',
    page: 'cultura',
    category: 'Cultura',
    label: 'Series',
    title: 'Series em destaque ganham ficha unica de acompanhamento para episodios e bastidores',
    summary:
      'O portal passou a concentrar contexto, cronologia e novas chamadas em uma mesma estrutura de leitura.',
    excerpt:
      'A proposta e evitar que a cobertura de series fique dispersa em notas isoladas e sem conexao.',
    author: 'Nucleo de Entretenimento',
    publishedAt: '20 abr 2026, 11h20',
    readTime: '4 min',
    location: 'Sao Paulo',
    tags: ['series', 'entretenimento', 'cronologia'],
    body: [
      'A cobertura de series em destaque passou a contar com uma ficha unica de acompanhamento para reunir episodios, cronologia e bastidores em um mesmo bloco editorial. O objetivo e evitar fragmentacao da leitura.',
      'Cada nova materia pode ser encaixada nessa mesma estrutura, preservando o contexto e reduzindo repeticao. A pagina da editoria passa a funcionar como ponto de entrada permanente para quem acompanha o tema.',
      'A equipe avalia que o modelo tambem pode ser replicado para musica e cinema quando houver cobertura recorrente ao longo de varias semanas.',
    ],
  },
  {
    slug: 'coluna-de-critica-passa-a-aparecer-ao-lado-da-agenda',
    page: 'cultura',
    category: 'Cultura',
    label: 'Critica',
    title: 'Coluna de critica passa a aparecer ao lado da agenda para equilibrar servico e analise',
    summary:
      'A editoria decidiu aproximar recomendacao pratica e leitura opinativa em uma mesma pagina de acompanhamento.',
    excerpt:
      'A combinacao tenta oferecer ao leitor tanto programacao quanto interpretacao dos lancamentos.',
    author: 'Mesa de Cultura',
    publishedAt: '20 abr 2026, 14h00',
    readTime: '3 min',
    location: 'Salvador',
    tags: ['critica', 'agenda', 'cultura'],
    body: [
      'A pagina de cultura passou a exibir a coluna de critica ao lado da agenda para equilibrar informacao de servico e analise de lancamentos. A alteracao busca aproximar diferentes modos de leitura sem dividir a editoria em areas isoladas.',
      'Com isso, um mesmo tema pode aparecer com data de estreia, referencia de programacao e texto analitico em uma estrutura compartilhada. O leitor decide se quer seguir pelo servico ou pelo aprofundamento.',
      'A equipe considera que esse formato fortalece a pagina fixa da categoria como ambiente recorrente, e nao apenas como colecao de notas soltas.',
    ],
  },
  {
    slug: 'agenda-do-congresso-ganha-monitoramento-por-etapa',
    page: 'politica',
    category: 'Politica',
    label: 'Congresso',
    title: 'Agenda do Congresso ganha monitoramento por etapa para acompanhar votacoes e relatorias',
    summary:
      'A pagina de politica passou a ordenar a cobertura conforme o ponto em que cada proposta se encontra no processo legislativo.',
    excerpt:
      'A mudanca tenta evitar confusao entre anuncios preliminares e medidas ja em fase decisoria.',
    author: 'Editoria de Politica',
    publishedAt: '20 abr 2026, 08h30',
    readTime: '5 min',
    location: 'Brasilia',
    tags: ['congresso', 'votacao', 'agenda'],
    body: [
      'A cobertura do Congresso passou a ser organizada por etapa de tramitacao para deixar mais claro em que ponto se encontra cada proposta acompanhada pela editoria. O formato diferencia debate inicial, relatoria, votacao e desdobramento institucional.',
      'Com isso, o leitor consegue identificar se um tema esta apenas em articulacao ou se ja entrou em fase de decisao. A equipe considera esse filtro importante para evitar interpretacoes apressadas sobre andamento de medidas.',
      'A estrutura tambem sera usada quando a pagina fixa de politica passar a receber materias a partir do banco, preservando a cronologia do processo legislativo.',
    ],
  },
  {
    slug: 'bastidores-do-executivo-passam-a-ser-reunidos-em-trilha-propria',
    page: 'politica',
    category: 'Politica',
    label: 'Executivo',
    title: 'Bastidores do Executivo passam a ser reunidos em trilha propria de acompanhamento',
    summary:
      'Notas dispersas sobre articulacao politica agora entram em uma sequencia unica de leitura dentro da editoria.',
    excerpt:
      'A organizacao por trilha ajuda a recuperar antecedentes e a medir continuidade dos movimentos do governo.',
    author: 'Nucleo de Brasilia',
    publishedAt: '20 abr 2026, 10h10',
    readTime: '4 min',
    location: 'Brasilia',
    tags: ['executivo', 'articulacao', 'governo'],
    body: [
      'A editoria de politica passou a reunir bastidores do Executivo em uma trilha unica de acompanhamento para evitar que notas de articulacao fiquem dispersas em diferentes pontos do portal. O leitor passa a acompanhar o tema como sequencia, e nao como entradas isoladas.',
      'Cada novo movimento pode ser anexado a um historico anterior, preservando antecedentes e deixando mais claro o que mudou em relacao ao quadro anterior.',
      'O modelo foi pensado para funcionar de forma estavel quando os dados da cobertura forem carregados diretamente do banco, com ordenacao automatica por data e relevancia.',
    ],
  },
  {
    slug: 'julgamentos-relevantes-ganham-resumo-de-contexto-na-pagina',
    page: 'politica',
    category: 'Politica',
    label: 'Judiciario',
    title: 'Julgamentos relevantes ganham resumo de contexto e cronologia na pagina de politica',
    summary:
      'O portal passou a exibir antecedentes e pontos de decisao em blocos de apoio para cobertura institucional.',
    excerpt:
      'A medida ajuda a contextualizar processos longos sem repetir explicacoes em todas as materias.',
    author: 'Equipe de Politica',
    publishedAt: '20 abr 2026, 12h40',
    readTime: '4 min',
    location: 'Brasilia',
    tags: ['judiciario', 'cronologia', 'decisao'],
    body: [
      'A cobertura de julgamentos relevantes ganhou resumos de contexto e cronologia para acompanhar processos que se estendem por longos periodos. A editoria quer evitar repeticao excessiva de antecedentes em cada novo texto.',
      'Os blocos de apoio indicam os pontos principais da decisao, o historico recente e o que ainda falta para conclusao do caso. O recurso melhora a continuidade da leitura em temas institucionais mais complexos.',
      'Segundo a equipe, esse modelo deve ganhar importancia quando a pagina de artigo passar a buscar automaticamente do banco as relacoes com cronologias e materias anteriores.',
    ],
  },
  {
    slug: 'laboratorios-ampliam-parcerias-para-compartilhar-dados',
    page: 'ciencia',
    category: 'Ciencia',
    label: 'Pesquisa',
    title: 'Laboratorios ampliam parcerias para compartilhar dados e acelerar etapas de pesquisa',
    summary:
      'Instituicoes passaram a integrar bases e resultados preliminares em uma rede de colaboracao mais continua.',
    excerpt:
      'A cooperacao busca reduzir retrabalho e ampliar comparacao entre diferentes grupos.',
    author: 'Editoria de Ciencia',
    publishedAt: '20 abr 2026, 08h25',
    readTime: '5 min',
    location: 'Campinas',
    tags: ['laboratorios', 'pesquisa', 'dados'],
    body: [
      'Laboratorios de diferentes instituicoes ampliaram a troca de dados e resultados preliminares para acelerar etapas de pesquisa que dependem de comparacao entre grupos. A cooperacao foi desenhada para reduzir retrabalho e encurtar ciclos de validacao.',
      'Em vez de operar com bases isoladas, as equipes passam a integrar informacoes em rede, o que facilita revisao de metodo e acompanhamento dos achados ao longo do projeto.',
      'Para a editoria de ciencia, a iniciativa mostra como a cobertura pode se beneficiar de paginas fixas que preservem antecedentes, metodo e desdobramentos de uma mesma linha de estudo.',
    ],
  },
  {
    slug: 'missao-academica-organiza-cronologia-de-novas-etapas-orbitais',
    page: 'ciencia',
    category: 'Ciencia',
    label: 'Espaco',
    title: 'Missao academica organiza cronologia de novas etapas orbitais e resultados preliminares',
    summary:
      'Pesquisadores passaram a divulgar marcos do projeto em ordem de execucao para facilitar acompanhamento publico.',
    excerpt:
      'A cronologia ajuda a entender o que ja foi concluido e o que ainda depende de nova rodada de testes.',
    author: 'Nucleo de Ciencia',
    publishedAt: '20 abr 2026, 10h35',
    readTime: '4 min',
    location: 'Sao Jose dos Campos',
    tags: ['espaco', 'missao', 'cronologia'],
    body: [
      'Uma missao academica ligada a pesquisa espacial passou a divulgar suas etapas em cronologia detalhada para facilitar o acompanhamento publico do projeto. O material informa marcos concluidos, proximas fases e pontos que ainda dependem de validacao.',
      'A medida ajuda a reduzir a distancia entre anuncio institucional e compreensao do andamento tecnico. O leitor consegue identificar o que e resultado consolidado e o que ainda esta em fase de teste.',
      'A equipe do portal pretende usar a mesma logica na pagina fixa de ciencia, com blocos preparados para exibir fases de projeto e seus desdobramentos.',
    ],
  },
  {
    slug: 'universidades-criam-faixa-fixa-para-explicar-novos-estudos',
    page: 'ciencia',
    category: 'Ciencia',
    label: 'Academia',
    title: 'Universidades criam faixa fixa para explicar novos estudos ao publico geral',
    summary:
      'Os materiais reescrevem metodo, amostra e limites da pesquisa em linguagem mais acessivel.',
    excerpt:
      'A iniciativa tenta aproximar producao academica e leitura publica sem perder rigor.',
    author: 'Equipe de Ciencia e Dados',
    publishedAt: '20 abr 2026, 13h00',
    readTime: '4 min',
    location: 'Belo Horizonte',
    tags: ['universidades', 'estudos', 'divulgacao cientifica'],
    body: [
      'Universidades passaram a adotar uma faixa fixa de divulgacao para explicar novos estudos ao publico geral com linguagem mais acessivel. O material resume metodo, amostra e limites de cada pesquisa sem abrir mao do rigor informativo.',
      'A estrategia tenta aproximar producao academica e interesse publico, especialmente em temas que circulam rapidamente em redes e podem perder contexto quando sao resumidos em poucas linhas.',
      'A cobertura do portal acompanha essa tendencia como referencia para futuras paginas de artigo que recebam automaticamente dados estruturados sobre estudo, autores e escopo da pesquisa.',
    ],
  },
  {
    slug: 'entrevistas-curtas-passam-a-abrir-a-faixa-principal-de-videos',
    page: 'videos',
    category: 'Videos',
    label: 'Entrevistas',
    title: 'Entrevistas curtas passam a abrir a faixa principal de videos do portal',
    summary:
      'A editoria de videos passou a priorizar conversas objetivas com contexto resumido na primeira dobra da pagina.',
    excerpt:
      'O formato tenta equilibrar apelo visual, clareza editorial e continuidade com a cobertura escrita.',
    author: 'Editoria de Videos',
    publishedAt: '20 abr 2026, 09h00',
    readTime: '3 min',
    location: 'Sao Paulo',
    tags: ['entrevistas', 'videos', 'formato'],
    body: [
      'A editoria de videos passou a destacar entrevistas curtas na primeira faixa da pagina para combinar apelo visual com contexto resumido. A ideia e abrir a navegacao com um formato objetivo e de facil consumo.',
      'Cada clipe recebe chamada curta, indicacao de assunto e conexao com a cobertura escrita correspondente. O leitor pode partir do video para a materia completa sem perder o fio da apuracao.',
      'O modelo foi pensado para ser abastecido por dados do banco no futuro, com cada video ocupando automaticamente seu bloco conforme categoria e prioridade.',
    ],
  },
  {
    slug: 'cortes-de-cobertura-ganham-vinculo-direto-com-materias',
    page: 'videos',
    category: 'Videos',
    label: 'Cobertura',
    title: 'Cortes de cobertura ganham vinculo direto com materias para leitura complementar',
    summary:
      'O portal passou a relacionar trechos em video com reportagens e analises da mesma pauta.',
    excerpt:
      'A costura entre video e texto foi desenhada para ampliar continuidade da experiencia editorial.',
    author: 'Nucleo Audiovisual',
    publishedAt: '20 abr 2026, 11h15',
    readTime: '4 min',
    location: 'Rio de Janeiro',
    tags: ['cortes', 'video', 'materias'],
    body: [
      'Os cortes de cobertura publicados na editoria de videos passaram a exibir vinculo direto com reportagens e analises relacionadas. A integracao quer ampliar a continuidade da experiencia entre diferentes formatos.',
      'Na pratica, um mesmo assunto pode ser acompanhado por clipe curto, texto principal e leitura de contexto, sem que o leitor precise reconstruir sozinho a conexao entre essas pecas.',
      'A equipe considera que esse encadeamento sera ainda mais relevante quando o banco passar a alimentar automaticamente as relacoes entre materia, tag e asset de video.',
    ],
  },
  {
    slug: 'playlist-tematica-organiza-especiais-em-sequencia-editorial',
    page: 'videos',
    category: 'Videos',
    label: 'Serie',
    title: 'Playlist tematica organiza especiais em sequencia editorial dentro da pagina',
    summary:
      'A editoria passou a agrupar episodios e entradas curtas em blocos permanentes por assunto.',
    excerpt:
      'A navegacao por serie permite ao leitor retomar a cobertura audiovisual por tema.',
    author: 'Equipe de Conteudo Visual',
    publishedAt: '20 abr 2026, 13h25',
    readTime: '3 min',
    location: 'Sao Paulo',
    tags: ['playlist', 'especiais', 'serie'],
    body: [
      'A pagina de videos passou a agrupar especiais e episodios em playlists tematicas para reforcar a leitura por assunto. O leitor encontra uma sequencia editorial clara em vez de uma lista unica de publicacoes.',
      'A organizacao por serie melhora a retomada de temas recorrentes e ajuda o portal a preservar historico audiovisual quando uma pauta ganha novos capitulos.',
      'No desenho futuro, as playlists poderao ser alimentadas pelo banco e montadas automaticamente conforme a relacao entre materia, video e tags do mesmo tema.',
    ],
  },
]

export function getCategoryContent(page) {
  return categoryPageContent[page] ?? null
}

export function getArticlesByPage(page) {
  return articleRecords.filter((article) => article.page === page)
}

export function getArticleBySlug(slug) {
  return articleRecords.find((article) => article.slug === slug) ?? null
}

export function getRelatedArticles(article, limit = 3) {
  if (!article) {
    return []
  }

  return articleRecords
    .filter((item) => item.page === article.page && item.slug !== article.slug)
    .slice(0, limit)
}
