# Histórico de versões

## 2.7.0

- Nova aba Cortes para vídeo, áudio e GIF.
- Campos de início e fim em segundos ou `HH:MM:SS.000`, com fim opcional.
- Vídeo e áudio usam cópia direta dos fluxos, faixas e metadados, sem recompressão.
- GIF é recodificado mantendo resolução e animação, com publicação temporária segura.
- Pasta de cortes lembrada automaticamente.
- Testes cobrindo vídeo, áudio, GIF, validação de intervalo e preservação do original.

## 2.6.1

- Adicionada a marca discreta `frstt.dev` no cabeçalho do aplicativo e na apresentação do projeto.

## 2.6.0

### Interface

- Tema grafite com identidade violeta, navegação superior e cartões de opções.
- Áreas Conversor e Discord reorganizadas, com rolagem para telas menores.
- Botões de conversão e cancelamento sempre acessíveis.
- Configurações protegidas enquanto uma tarefa está em andamento.

### Conversão

- Exportação de GIF para Discord com paleta global e processamento sequencial pelo FFmpeg.
- Progresso por quadro durante a codificação e tempo decorrido por etapa.
- Mensagem com tamanho obtido e meta quando a animação não cabe.
- Cancelamento também no conversor geral, sem publicar arquivos incompletos de uma conversão interrompida.
- Preferências de pasta e FPS preservadas.

### Validação

- 12 testes automatizados: conversão, dimensões, transparência, duração de GIF, vídeo a 60 FPS, cancelamento, nomes repetidos, pastas e interface.
- Instalador inclui ImageMagick e FFmpeg; não exige Python no computador de destino.

GIFs longos podem ultrapassar a meta do Discord mesmo após a redução de cores. O aplicativo não corta a duração nem descarta quadros para fazê-los caber.
