# Taxonomia do corpus — Assuntos oficiais da CVM

O corpus regulatório do projeto é organizado pelos **32 assuntos oficiais** da seção
"Lista de Assuntos" do portal de normas da CVM
(<https://conteudo.cvm.gov.br/legislacao/resolucoes.html>). Os nomes abaixo são mantidos
exatamente como aparecem no portal e são os mesmos gravados na tabela `temas` do banco
(`db/init.sql` e `db/migrations/001_temas.sql`).

## Por que seguir a classificação oficial da CVM

A organização do corpus adota a classificação temática oficial publicada pela própria CVM em vez
de uma taxonomia criada pelo projeto. Essa escolha tem três motivos. Primeiro, a
**reprodutibilidade**: o critério de inclusão de cada norma é verificável por qualquer pessoa no
portal oficial, sem depender de julgamento subjetivo do pesquisador, o que permite que outro
trabalho reconstrua o mesmo recorte. Segundo, a **rastreabilidade e a atualização**: como o
portal já associa cada resolução a um ou mais assuntos, a coleta automatizada pode partir
diretamente das buscas filtradas por assunto, e novas normas publicadas pela autarquia entram no
tema correto sem reclassificação manual. Terceiro, a **validade de domínio**: a classificação
reflete a forma como o próprio regulador estrutura sua produção normativa e como os
participantes do mercado consultam as normas, o que torna os temas adequados tanto para
delimitar o escopo do RAG quanto para avaliar suas respostas por área. Como uma mesma norma pode
pertencer a mais de um assunto (por exemplo, a Resolução CVM 232 está em "Companhias Abertas" e
em "Ofertas Públicas"), o banco modela a relação entre normas e temas como N:N. A priorização em
núcleo, segunda leva e fora do escopo permite uma coleta incremental, começando pelos assuntos de
maior impacto para investidores e emissores e excluindo os assuntos de organização interna da
autarquia, que não tratam da regulação do mercado.

## Prioridades

| Prioridade (valor no banco) | Significado |
|---|---|
| `nucleo` | Lote piloto desta etapa. |
| `segunda_leva` | Demais assuntos ligados a participantes do mercado e produtos; coleta após aprovação do piloto. |
| `fora_do_escopo` | Assuntos internos da CVM; não entram no RAG. |

## Os 32 assuntos

A coluna **tag** é o valor do parâmetro `tags` usado pelo portal na busca filtrada. Ele nem
sempre é igual ao nome exibido (ver notas para o scraper abaixo).

| # | Assunto | Prioridade | Tag no portal | Busca filtrada |
|---|---|---|---|---|
| 1 | Administradores de Carteiras de Valores Mobiliários | segunda_leva | `Administradores de Carteiras` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Administradores%20de%20Carteiras) |
| 2 | Agências de Classificação de Risco de Crédito | segunda_leva | `Agencias de Classificacao de Risco de Credito` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Agencias%20de%20Classificacao%20de%20Risco%20de%20Credito) |
| 3 | Agentes Fiduciários | segunda_leva | `Agentes Fiduciarios` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Agentes%20Fiduciarios) |
| 4 | Analistas de Valores Mobiliários | segunda_leva | `Analistas de Valores Mobiliarios` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Analistas%20de%20Valores%20Mobiliarios) |
| 5 | Assessores de Investimento | segunda_leva | `Assessores de Investimento` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Assessores%20de%20Investimento) |
| 6 | Atos expedidos pela CVM | fora_do_escopo | `Atos expedidos pela CVM` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Atos%20expedidos%20pela%20CVM) |
| 7 | Auditores Independentes | segunda_leva | `Auditor Independente` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Auditor%20Independente) |
| 8 | BDR | segunda_leva | `BDR` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=BDR) |
| 9 | Cadastro de Investidores e PLD/FTP | nucleo | `Cadastro de Investidores` e `PLD/FTP` | [Cadastro de Investidores](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Cadastro%20de%20Investidores) · [PLD/FTP](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=PLD/FTP) |
| 10 | Cadastro de Participantes Regulados | fora_do_escopo | `Cadastro de Participantes Regulados` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Cadastro%20de%20Participantes%20Regulados) |
| 11 | Clubes de Investimento | segunda_leva | `Clubes de Investimento` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Clubes%20de%20Investimento) |
| 12 | Companhias Abertas | nucleo | `Companhia` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Companhia) |
| 13 | Companhias Securitizadoras | segunda_leva | `Companhias Securitizadoras` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Companhias%20Securitizadoras) |
| 14 | Consultores de Valores Mobiliários | segunda_leva | `Consultores de Valores Mobiliarios` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Consultores%20de%20Valores%20Mobiliarios) |
| 15 | Fundos de Investimento | nucleo | `Fundos de Investimento` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Fundos%20de%20Investimento) |
| 16 | Identidade Visual Institucional | fora_do_escopo | `Identidade Visual Institucional` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Identidade%20Visual%20Institucional) |
| 17 | Infraestrutura do Mercado | segunda_leva | `Infraestrutura do Mercado` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Infraestrutura%20do%20Mercado) |
| 18 | Intermediários | nucleo | `Intermediários` (codificado `Intermedi%E1rios`) | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Intermedi%E1rios) |
| 19 | Investidores Não Residentes | segunda_leva | `Investidores Nao Residentes` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Investidores%20Nao%20Residentes) |
| 20 | Mercados Organizados | segunda_leva | `Mercados Organizados` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Mercados%20Organizados) |
| 21 | Normas Contábeis | segunda_leva | `Normas Contabeis` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Normas%20Contabeis) |
| 22 | Ofertas Públicas | nucleo | `Ofertas Publicas` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Ofertas%20Publicas) |
| 23 | Ouvidoria | fora_do_escopo | `Ouvidoria` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Ouvidoria) |
| 24 | Portabilidade | segunda_leva | `Portabilidade` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Portabilidade) |
| 25 | Regimento Interno | fora_do_escopo | `Regimento Interno` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Regimento%20Interno) |
| 26 | Ritos Processuais | fora_do_escopo | `Ritos Processuais` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Ritos%20Processuais) |
| 27 | Sandbox Regulatório | segunda_leva | `Sandbox Regulatório` (codificado `Sandbox%20Regulat%F3rio`) | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Sandbox%20Regulat%F3rio) |
| 28 | Sistema Integrado de Gestão de Riscos da CVM | fora_do_escopo | `Sistema Integrado de Gestão de Riscos da CVM` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Sistema%20Integrado%20de%20Gest%E3o%20de%20Riscos%20da%20CVM) |
| 29 | Sistemas de Gestão Institucional da CVM | fora_do_escopo | `Sistemas de Gestão Institucional da CVM` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Sistemas%20de%20Gest%E3o%20Institucional%20da%20CVM) |
| 30 | Sociedades beneficiárias de recursos oriundos de incentivos fiscais (Cias. Incentivadas) | fora_do_escopo | `Companhias Incentivadas` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Companhias%20Incentivadas) |
| 31 | Suitability | nucleo | `Suitability` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Suitability) |
| 32 | Taxas, Débitos e Restituições | fora_do_escopo | `Taxas/Débitos/Restituições` | [link](https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=Taxas/D%E9bitos/Restitui%E7%F5es) |

Resumo: 6 assuntos no núcleo, 16 na segunda leva e 10 fora do escopo.

## Notas para o scraper

Levantadas no portal em 18/11/2026.

- **Padrão da busca filtrada:**
  `https://conteudo.cvm.gov.br/legislacao/index.html?buscado=true&pasta=resolucoes&filtro=todos&contCategoriasCheck=1&vimDaCategoria=/legislacao/resolucoes/&tags=<tag>`.
  Os links originais do portal têm uma barra dupla depois do domínio (`.gov.br//legislacao`) e
  espaços não codificados; acima eles foram normalizados (barra simples e `%20`), forma que foi
  testada e responde normalmente.
- **A tag não é o nome do assunto.** Exemplos: "Companhias Abertas" → `Companhia`;
  "Auditores Independentes" → `Auditor Independente`; "Cias. Incentivadas" →
  `Companhias Incentivadas`. A maioria das tags vem sem acento; as que têm acento estão
  codificadas em **Latin-1** (`%E1` = á, `%E3` = ã, `%F3` = ó, `%E9` = é, `%E7` = ç, `%F5` = õ),
  não em UTF-8.
- **"Cadastro de Investidores e PLD/FTP" tem duas tags.** No portal, esse assunto aparece como
  um item só com dois links. Por isso a "Lista de Assuntos" tem 33 links para 32 assuntos. O
  scraper deve consultar as duas tags e juntar os resultados no mesmo tema.
- **A busca é paginada.** Ex.: "Ofertas Públicas" tinha 13 resultados em 2 páginas; o controle
  "Próxima" não expõe a URL diretamente.
- **Normas revogadas continuam na listagem**, com "(Revogada)" no título (ex.: Resoluções 39
  e 85). O scraper deve preencher `status_vigencia` a partir disso.
- **Página da norma:** `https://conteudo.cvm.gov.br/legislacao/resolucoes/resolNNN.html` (número
  com 3 dígitos). O assunto aparece no rodapé da página como a mesma tag da busca.
- **PDF:** fica em `/export/sites/cvm/legislacao/resolucoes/anexos/<pasta>/resolNNN[consolid].pdf`,
  onde `<pasta>` muda por faixa de número (`001`, `100`, `200`). Isso não é documentado, então o
  scraper deve ler o link na página da norma em vez de montar a URL. Normas que já foram alteradas
  têm texto consolidado (`resolNNNconsolid.pdf`); as demais só têm o original (`resolNNN.pdf`).
- O lote em si (normas escolhidas por assunto do núcleo) está em `data_lake/manifesto.csv`.
