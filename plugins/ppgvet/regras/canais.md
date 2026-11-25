# Canais e links (perfis, sites e UTM)

Adaptado dos guias de redes e de UTM da PPGVET (o dono fica com quem cuida do pacote; mudou lá, muda aqui). Só o que já é público.

## Perfis e sites
| | Instagram | YouTube | outros | site |
|---|---|---|---|---|
| PPGVET | https://www.instagram.com/ppgvet_oficial/ | https://www.youtube.com/@ppgveteducacao | https://www.facebook.com/ppgvet.oficial · https://www.tiktok.com/@ppgvet_oficial · https://www.linkedin.com/school/ppgvet-agro-educa%C3%A7%C3%A3o/ | https://site.ppgvet.com.br/ |
| PPG Educação | https://www.instagram.com/ppg.educacao/ | usa o da PPGVET | sem Facebook; TikTok e LinkedIn: os da PPGVET | https://site.ppgeducacao.com.br/ |

| podcast (da PPGVET) | Instagram | YouTube | Spotify | Apple | página |
|---|---|---|---|---|---|
| O Aviário | https://www.instagram.com/oaviariopodcast/ | https://www.youtube.com/@oaviariopodcast | https://open.spotify.com/show/3e6el6JYY3agUb5VCuvdSD | https://podcasts.apple.com/br/podcast/id1655963633 | https://site.ppgvet.com.br/oaviario |
| SuinoCast | https://www.instagram.com/suinocast/ | https://www.youtube.com/@SuinoCast | https://open.spotify.com/show/35pO5mnZ414tCj8osygXti | https://podcasts.apple.com/br/podcast/id1454819334 | https://site.ppgvet.com.br/suinocast |
| +Rúmen | https://www.instagram.com/maisrumenpc/ | https://www.youtube.com/@maisrumenpodcast | https://open.spotify.com/show/2L9zDyQjcmKqph7M9WYD4r | https://podcasts.apple.com/br/podcast/id1664112475 | https://site.ppgvet.com.br/maisrumen |
| PetFood | https://www.instagram.com/petfoodpodcast/ | https://www.youtube.com/@PetFoodPodcast | https://open.spotify.com/show/4CQZA21sKdNmA45aShq6Nx | https://podcasts.apple.com/br/podcast/id1808496602 | https://site.ppgvet.com.br/petfood |

Página de cada pós: `https://site.ppgvet.com.br/pos-<sigla>` (PPGVET) e `https://site.ppgeducacao.com.br/pos-<sigla>` (PPG), sigla em minúsculo (`marca.md`).

## Link com UTM
- **Todo link que sai à mão** (bio, story, post, descrição de vídeo, QR, WhatsApp) sai do gerador "Links com UTM" do sistema. A regra abaixo serve para conferir o link e, sem o gerador à mão, montar e avisar a pessoa para conferir nele.
- Só página de site nosso (`*.ppgvet.com.br`, `*.ppgeducacao.com.br`) recebe UTM. Link entre os nossos sites e link para fora (YouTube, Spotify, Apple) vão sem.
- Anúncio: o UTM vai no modelo de parâmetros da plataforma (no gerador), nunca no link; é do responsável pelo tráfego.
- Teste: `utm_source=teste…`, nunca link real.

| campo | regra | exemplo |
|---|---|---|
| `utm_source` | `<rede>-<perfil>`; WhatsApp e e-mail, só a rede | `instagram-ppgvet`, `youtube-ppgvet`, `whatsapp`, `email` |
| `utm_medium` | fixo pela rede | `social` (YouTube também); e-mail `email` |
| `utm_campaign` | a ação de marketing; minúsculo, hífen, sem número; data no fim só para separar edições que se repetem | `escola`, `live`, `natal-dez-2026` |
| `utm_content` | onde o link fica ou qual peça; story e direct começam por `story`/`dm`; QR leva `qr-code` antes da data | `bio`, `story-sorteio`, `bio-qr-code-nov-2026` |

Perfis no `utm_source`: Instagram `ppgvet`, `ppgeducacao`, `aviario`, `suinocast`, `maisrumen`, `petfood`, `avesesuinos`, `academiadapecuaria`, `academiasuina` · TikTok e LinkedIn `ppgvet` · YouTube `ppgvet`, `aviario`, `suinocast`, `maisrumen`, `petfood`. Perfil pessoal de diretor: pelo gerador.
