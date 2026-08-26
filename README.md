<div align="center">
  <img src="docs/banner.png" alt="Vsy Converter" width="100%">

  <p><strong>Conversão de imagens simples, rápida e sem terminal.</strong></p>

  ![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-6d3cff?style=for-the-badge&logo=windows11&logoColor=white)
  ![Versão](https://img.shields.io/badge/versão-2.4.0-b05cff?style=for-the-badge)
  ![ImageMagick](https://img.shields.io/badge/ImageMagick-7.1-8a4fff?style=for-the-badge)

  <br><br>
  <a href="https://github.com/frsttw/vsy-converter/releases/latest/download/Instalador-Vsy-Converter.exe">
    <img src="https://img.shields.io/badge/BAIXAR%20PARA%20WINDOWS-9f50e8?style=for-the-badge&logo=windows11&logoColor=white" alt="Baixar Vsy Converter">
  </a>
</div>

## Sobre

O **Vsy Converter** oferece uma interface gráfica para o ImageMagick e o FFmpeg. Converta imagens e transforme vídeos em GIF sem memorizar comandos ou abrir o terminal.

## Destaques

- Conversão de vários arquivos em uma única operação.
- Suporte a JPG, PNG, WebP, AVIF, GIF, BMP, TIFF, ICO e PDF.
- Controle de qualidade com resultado visível e previsível.
- Redimensionamento com preservação automática da proporção.
- Opção para manter ou remover metadados.
- Proteção dos arquivos originais e numeração automática de nomes repetidos.
- Memória automática da pasta de destino para cada tipo de saída.
- Conversão para GIF de formatos de vídeo modernos, antigos, profissionais e de celular suportados pelo FFmpeg.
- Controle de fluidez do GIF entre 10 e 60 FPS, com preferência memorizada.
- Interface escura, responsiva e inteiramente em português.
- Instalador completo com o ImageMagick incluído.

## Como usar

1. Adicione uma ou mais imagens.
2. Escolha o formato de saída e a qualidade.
3. Se desejar, ative o redimensionamento.
4. Selecione a pasta de destino.
5. Pressione **Converter agora**.

## Formatos

| Tipo | Entrada | Saída |
|---|---|---|
| Imagens | JPG, PNG, WebP, AVIF, GIF, BMP, TIFF, HEIC, SVG, PSD, RAW e outros | JPG, PNG, WebP, AVIF, GIF, BMP, TIFF, ICO e PDF |
| Vídeos | MP4, MKV, MOV, AVI, WebM, WMV, MPEG, MTS, VOB, 3GP e outros formatos reconhecidos pelo FFmpeg | GIF de 10 a 60 FPS |

> A disponibilidade de formatos especiais de imagem depende dos codecs incluídos no ImageMagick. Os vídeos são validados diretamente pelo FFmpeg.

## Instalação

Baixe `Instalador-Vsy-Converter.exe` na seção **Releases** e siga o assistente. O pacote inclui ImageMagick e FFmpeg e cria um atalho na Área de Trabalho.

As preferências de pasta e FPS das versões anteriores são preservadas na atualização.

## Tecnologias

- Python e Tkinter para a aplicação desktop.
- ImageMagick como mecanismo de conversão.
- FFmpeg para leitura e conversão de vídeos.
- PyInstaller para o executável.
- Inno Setup para o instalador do Windows.

Os avisos e links das licenças estão em [`LICENCAS-DE-TERCEIROS.txt`](LICENCAS-DE-TERCEIROS.txt).

## Construção local

Com Python 3, PyInstaller e Inno Setup 6 instalados, execute:

```powershell
.\build-installer.ps1
```

O instalador será criado em `installer-output`.

## Estrutura

```text
Vsy Converter
├── app.py                  # Aplicação desktop
├── assets/                 # Identidade visual e ícone
├── docs/                   # Materiais da página do projeto
├── build-installer.ps1     # Automação da compilação
└── installer.iss           # Configuração do instalador
```

---

<div align="center">
  Desenvolvido por <a href="https://github.com/frsttw">@frsttw</a>
</div>
