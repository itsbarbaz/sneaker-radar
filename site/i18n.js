/* Hypewise: lingue del sito. Inglese (USA) di default, le altre si scelgono dal menu. */
(function () {
  var LANGS = [
    ["en", "English", "en-US"],
    ["es", "Español", "es-ES"],
    ["fr", "Français", "fr-FR"],
    ["it", "Italiano", "it-IT"],
    ["ru", "Русский", "ru-RU"]
  ];

  var D = {
  en: {
    "nav.how": "How it works", "nav.signal": "The signal", "nav.cover": "What we track", "nav.open": "Open the board",
    "hero.eyebrow": "Sneaker resale prices, USA",
    "hero.h1": "Buy with your <em>head.</em>",
    "hero.lead": "Hypewise tracks resale prices for the most in-demand sneakers in the United States every day. See whether a pair is rising, falling or flat, in dollars, without opening ten different sites.",
    "hero.cta2": "How it works",
    "card.tag": "Sample card", "card.tag2": "30 days", "card.chg": "-4.2% in 7 days", "card.v": "Wait",
    "card.vp": "The price has been falling for 2 weeks. Better to wait until it settles.",
    "card.fine": "Illustrative example. Prices and chart are not real data.",
    "how.h": "How it works", "how.intro": "Three steps, all automatic. Data refreshes on its own.",
    "s1.n": "STEP 1", "s1.h": "We collect prices", "s1.p": "We read average market prices in US dollars for 50 of the most in-demand models. Each model is refreshed every 1-2 days.",
    "s2.n": "STEP 2", "s2.h": "We check every listing", "s2.p": "We discard results with the wrong model or brand, socks and accessories, outdated data and out-of-range prices. We keep only pairs we can trust.",
    "s3.n": "STEP 3", "s3.h": "We show you the trend", "s3.p": "For each pair you see today's price, the 7-day change and the trend over time, so you can tell at a glance what is moving.",
    "sig.h": "The signal", "sig.soon": "coming soon",
    "sig.intro": "For every pair, Hypewise will read the chart and give you a clear call, with the reason written underneath. Never a random sentence: each signal explains what it is based on.",
    "cop.name": "Cop", "cop.p": "The price is near its recent low and the drop is slowing. It may be a good time to buy.",
    "wait.name": "Wait", "wait.p": "The price is still falling, or the signals disagree. Better to watch a few more days.",
    "sell.name": "Sell", "sell.p": "The price is near its recent high and the climb is slowing. It may be a good time to sell.",
    "sig.fine": "These are automatic estimates based on past prices, meant to help you think. They are not financial advice and should not be taken literally. When there is little data, Hypewise says so instead of giving a call.",
    "cov.h": "What we track", "cov.intro": "For now we focus on sneakers, picked from the models that trade the most in the United States.",
    "cov.later": "Apparel: planned",
    "who1.h": "If you resell", "who1.p": "See where prices are moving before you stock up, and check whether the price you are offered is in line with the market.",
    "who2.h": "If you buy for yourself", "who2.p": "Know whether you are paying a high or low price compared with recent days, without being a market expert.",
    "final.h": "See what is moving today.",
    "foot1": "Prices are market estimates in USD calculated from StockX data supplied through KicksDB, and may differ from actual prices at the time of purchase. Hypewise does not provide financial advice.",
    "foot2": "Hypewise is not affiliated with or sponsored by StockX, Nike, Jordan, adidas or any other brand mentioned. Names belong to their respective owners.",
    "b.title": "Hypewise Prices",
    "b.sub": "US market prices in dollars, verified sneakers only. Updated every 1-2 days.",
    "b.demo": "SAMPLE DATA. Prices shown are examples, not real market data.",
    "b.search": "Search model or SKU", "b.all": "All", "b.brand": "Brand", "b.sortlabel": "Sort",
    "b.sort.move": "Biggest move", "b.sort.price": "Highest price", "b.sort.name": "Name",
    "b.nomatch": "No sneakers match these filters.", "b.nodata": "No prices saved yet. They are added on every update.",
    "b.stat1": "Models tracked", "b.stat2": "Brands", "b.stat3": "Moves over 5% in 7 days",
    "b.updated": "Updated", "b.collecting": "collecting", "b.spark": "Price trend", "b.summary": "Summary",
    "b.foot": "Average market price in USD (source: KicksDB / StockX). The change compares the latest price with the one from about 7 days earlier; \"collecting\" means at least two readings are still needed."
  },
  es: {
    "nav.how": "Cómo funciona", "nav.signal": "La señal", "nav.cover": "Qué seguimos", "nav.open": "Abrir el panel",
    "hero.eyebrow": "Precios de reventa de zapatillas, EE. UU.",
    "hero.h1": "Compra con la <em>cabeza.</em>",
    "hero.lead": "Hypewise sigue cada día los precios de reventa de las zapatillas más buscadas de Estados Unidos. Mira si un modelo sube, baja o se mantiene, en dólares, sin abrir diez webs distintas.",
    "hero.cta2": "Cómo funciona",
    "card.tag": "Ficha de ejemplo", "card.tag2": "30 días", "card.chg": "-4,2 % en 7 días", "card.v": "Espera",
    "card.vp": "El precio lleva 2 semanas bajando. Mejor esperar a que se estabilice.",
    "card.fine": "Ejemplo ilustrativo. Los precios y el gráfico no son datos reales.",
    "how.h": "Cómo funciona", "how.intro": "Tres pasos, todos automáticos. Los datos se actualizan solos.",
    "s1.n": "PASO 1", "s1.h": "Recogemos los precios", "s1.p": "Leemos los precios medios de mercado en dólares de 50 de los modelos más demandados. Cada modelo se actualiza cada 1-2 días.",
    "s2.n": "PASO 2", "s2.h": "Revisamos cada ficha", "s2.p": "Descartamos los resultados con modelo o marca incorrectos, calcetines y accesorios, datos antiguos y precios fuera de rango. Solo dejamos los pares de los que nos podemos fiar.",
    "s3.n": "PASO 3", "s3.h": "Te mostramos la tendencia", "s3.p": "De cada par ves el precio de hoy, la variación de 7 días y la evolución en el tiempo, para entender de un vistazo qué se mueve.",
    "sig.h": "La señal", "sig.soon": "próximamente",
    "sig.intro": "Para cada par, Hypewise leerá el gráfico y te dará una indicación clara, con el motivo escrito debajo. Nunca una frase al azar: cada señal explica en qué se basa.",
    "cop.name": "Cop", "cop.p": "El precio está cerca de su mínimo reciente y la bajada se frena. Puede ser buen momento para comprar.",
    "wait.name": "Espera", "wait.p": "El precio sigue bajando, o las señales se contradicen. Mejor observar unos días más.",
    "sell.name": "Sell", "sell.p": "El precio está cerca de su máximo reciente y la subida se frena. Puede ser buen momento para vender.",
    "sig.fine": "Son estimaciones automáticas basadas en precios pasados, pensadas para ayudarte a razonar. No son asesoramiento financiero ni deben tomarse al pie de la letra. Si hay pocos datos, Hypewise lo dice en lugar de dar una indicación.",
    "cov.h": "Qué seguimos", "cov.intro": "Por ahora nos centramos en zapatillas, elegidas entre los modelos que más se negocian en Estados Unidos.",
    "cov.later": "Ropa: en el plan",
    "who1.h": "Si revendes", "who1.p": "Ve hacia dónde se mueven los precios antes de comprar stock y comprueba si el precio que te ofrecen está en línea con el mercado.",
    "who2.h": "Si compras para ti", "who2.p": "Sabe si pagas un precio alto o bajo frente a los últimos días, sin ser experto en el mercado.",
    "final.h": "Mira qué se mueve hoy.",
    "foot1": "Los precios son estimaciones de mercado en USD calculadas con datos de StockX proporcionados por KicksDB y pueden diferir de los precios reales en el momento de la compra. Hypewise no ofrece asesoramiento financiero.",
    "foot2": "Hypewise no está afiliado ni patrocinado por StockX, Nike, Jordan, adidas ni ninguna otra marca citada. Los nombres pertenecen a sus respectivos propietarios.",
    "b.title": "Hypewise Precios",
    "b.sub": "Precios del mercado de EE. UU. en dólares, solo zapatillas verificadas. Actualizado cada 1-2 días.",
    "b.demo": "DATOS DE EJEMPLO. Los precios mostrados son ejemplos, no datos reales de mercado.",
    "b.search": "Buscar modelo o SKU", "b.all": "Todas", "b.brand": "Marca", "b.sortlabel": "Ordenar",
    "b.sort.move": "Mayor variación", "b.sort.price": "Precio más alto", "b.sort.name": "Nombre",
    "b.nomatch": "Ninguna zapatilla coincide con estos filtros.", "b.nodata": "Aún no hay precios guardados. Se añaden en cada actualización.",
    "b.stat1": "Modelos seguidos", "b.stat2": "Marcas", "b.stat3": "Movimientos de más del 5 % en 7 días",
    "b.updated": "Actualizado", "b.collecting": "recopilando", "b.spark": "Evolución del precio", "b.summary": "Resumen",
    "b.foot": "Precio medio de mercado en USD (fuente: KicksDB / StockX). La variación compara el último precio con el de hace unos 7 días; «recopilando» significa que faltan al menos dos lecturas."
  },
  fr: {
    "nav.how": "Comment ça marche", "nav.signal": "Le signal", "nav.cover": "Ce que nous suivons", "nav.open": "Ouvrir le tableau",
    "hero.eyebrow": "Prix de revente des sneakers, États-Unis",
    "hero.h1": "Achète avec la <em>tête.</em>",
    "hero.lead": "Hypewise suit chaque jour les prix de revente des sneakers les plus demandées aux États-Unis. Vois si un modèle monte, baisse ou stagne, en dollars, sans ouvrir dix sites différents.",
    "hero.cta2": "Comment ça marche",
    "card.tag": "Fiche d'exemple", "card.tag2": "30 jours", "card.chg": "-4,2 % en 7 jours", "card.v": "Attends",
    "card.vp": "Le prix baisse depuis 2 semaines. Mieux vaut attendre qu'il se stabilise.",
    "card.fine": "Exemple illustratif. Les prix et le graphique ne sont pas des données réelles.",
    "how.h": "Comment ça marche", "how.intro": "Trois étapes, toutes automatiques. Les données se mettent à jour toutes seules.",
    "s1.n": "ÉTAPE 1", "s1.h": "Nous collectons les prix", "s1.p": "Nous lisons les prix moyens du marché en dollars pour 50 des modèles les plus demandés. Chaque modèle est actualisé tous les 1 à 2 jours.",
    "s2.n": "ÉTAPE 2", "s2.h": "Nous vérifions chaque fiche", "s2.p": "Nous écartons les résultats avec un mauvais modèle ou une mauvaise marque, les chaussettes et accessoires, les données périmées et les prix aberrants. Nous ne gardons que les paires fiables.",
    "s3.n": "ÉTAPE 3", "s3.h": "Nous te montrons la tendance", "s3.p": "Pour chaque paire, tu vois le prix du jour, la variation sur 7 jours et l'évolution dans le temps, pour comprendre d'un coup d'œil ce qui bouge.",
    "sig.h": "Le signal", "sig.soon": "bientôt",
    "sig.intro": "Pour chaque paire, Hypewise lira le graphique et te donnera une indication claire, avec la raison écrite dessous. Jamais une phrase au hasard : chaque signal explique sur quoi il repose.",
    "cop.name": "Cop", "cop.p": "Le prix est proche de son plus bas récent et la baisse ralentit. Cela peut être le bon moment pour acheter.",
    "wait.name": "Attends", "wait.p": "Le prix baisse encore, ou les signaux se contredisent. Mieux vaut observer quelques jours de plus.",
    "sell.name": "Sell", "sell.p": "Le prix est proche de son plus haut récent et la hausse ralentit. Cela peut être le bon moment pour vendre.",
    "sig.fine": "Ce sont des estimations automatiques fondées sur les prix passés, destinées à t'aider à réfléchir. Ce ne sont pas des conseils financiers et il ne faut pas les prendre au pied de la lettre. Quand il y a peu de données, Hypewise le dit au lieu de donner une indication.",
    "cov.h": "Ce que nous suivons", "cov.intro": "Pour l'instant, nous nous concentrons sur les sneakers, choisies parmi les modèles les plus échangés aux États-Unis.",
    "cov.later": "Vêtements : prévu",
    "who1.h": "Si tu revends", "who1.p": "Vois où les prix évoluent avant de faire du stock, et vérifie si le prix qu'on te propose est cohérent avec le marché.",
    "who2.h": "Si tu achètes pour toi", "who2.p": "Sache si tu paies un prix élevé ou bas par rapport aux derniers jours, sans être expert du marché.",
    "final.h": "Vois ce qui bouge aujourd'hui.",
    "foot1": "Les prix sont des estimations de marché en USD calculées à partir de données StockX fournies via KicksDB et peuvent différer des prix réels au moment de l'achat. Hypewise ne fournit pas de conseil financier.",
    "foot2": "Hypewise n'est ni affilié à, ni sponsorisé par StockX, Nike, Jordan, adidas ou toute autre marque citée. Les noms appartiennent à leurs propriétaires respectifs.",
    "b.title": "Hypewise Prix",
    "b.sub": "Prix du marché américain en dollars, sneakers vérifiées uniquement. Mis à jour tous les 1 à 2 jours.",
    "b.demo": "DONNÉES D'EXEMPLE. Les prix affichés sont des exemples, pas des données réelles du marché.",
    "b.search": "Rechercher un modèle ou un SKU", "b.all": "Toutes", "b.brand": "Marque", "b.sortlabel": "Trier",
    "b.sort.move": "Plus forte variation", "b.sort.price": "Prix le plus élevé", "b.sort.name": "Nom",
    "b.nomatch": "Aucune sneaker ne correspond à ces filtres.", "b.nodata": "Aucun prix enregistré pour l'instant. Ils sont ajoutés à chaque mise à jour.",
    "b.stat1": "Modèles suivis", "b.stat2": "Marques", "b.stat3": "Variations de plus de 5 % en 7 jours",
    "b.updated": "Mis à jour le", "b.collecting": "en cours", "b.spark": "Évolution du prix", "b.summary": "Résumé",
    "b.foot": "Prix moyen du marché en USD (source : KicksDB / StockX). La variation compare le dernier prix à celui d'il y a environ 7 jours ; « en cours » signifie qu'il faut encore au moins deux relevés."
  },
  it: {
    "nav.how": "Come funziona", "nav.signal": "Il segnale", "nav.cover": "Cosa seguiamo", "nav.open": "Apri la bacheca",
    "hero.eyebrow": "Prezzi di rivendita delle sneaker, USA",
    "hero.h1": "Compra con la <em>testa.</em>",
    "hero.lead": "Hypewise segue ogni giorno i prezzi di rivendita delle sneaker più richieste negli Stati Uniti. Vedi se un modello sale, scende o resta fermo, in dollari, senza dover aprire dieci siti.",
    "hero.cta2": "Come funziona",
    "card.tag": "Scheda di esempio", "card.tag2": "30 giorni", "card.chg": "-4,2% in 7 giorni", "card.v": "Aspetta",
    "card.vp": "Il prezzo sta ancora scendendo da 2 settimane. Meglio aspettare che si stabilizzi.",
    "card.fine": "Esempio illustrativo. Prezzi e grafico non sono dati reali.",
    "how.h": "Come funziona", "how.intro": "Tre passaggi, tutti automatici. I dati si aggiornano da soli.",
    "s1.n": "PASSO 1", "s1.h": "Raccogliamo i prezzi", "s1.p": "Leggiamo i prezzi medi di mercato in dollari di 50 modelli tra i più richiesti. Ogni modello viene aggiornato ogni 1-2 giorni.",
    "s2.n": "PASSO 2", "s2.h": "Controlliamo ogni scheda", "s2.p": "Scartiamo i risultati con modello o marchio sbagliato, calzini e accessori, dati vecchi e prezzi fuori scala. Teniamo solo le scarpe di cui possiamo fidarci.",
    "s3.n": "PASSO 3", "s3.h": "Ti mostriamo l'andamento", "s3.p": "Per ogni scarpa trovi il prezzo di oggi, la variazione degli ultimi 7 giorni e l'andamento nel tempo. Così capisci a colpo d'occhio cosa si muove.",
    "sig.h": "Il segnale", "sig.soon": "in arrivo",
    "sig.intro": "Su ogni scarpa Hypewise leggerà il grafico e ti darà un'indicazione chiara, con il motivo scritto sotto. Non una frase a caso: ogni segnale spiega su cosa si basa.",
    "cop.name": "Cop", "cop.p": "Il prezzo è vicino al minimo recente e la discesa sta rallentando. Può essere un buon momento per comprare.",
    "wait.name": "Aspetta", "wait.p": "Il prezzo sta ancora scendendo, o i segnali sono contrastanti. Meglio guardare ancora qualche giorno.",
    "sell.name": "Sell", "sell.p": "Il prezzo è vicino al massimo recente e la salita sta rallentando. Può essere un buon momento per vendere.",
    "sig.fine": "Sono stime automatiche basate sui prezzi passati, pensate per aiutarti a ragionare. Non sono consigli finanziari e non vanno prese alla lettera. Se i dati sono pochi, Hypewise lo dice invece di dare un consiglio.",
    "cov.h": "Cosa seguiamo", "cov.intro": "Per ora ci concentriamo sulle sneaker, scelte tra i modelli che negli Stati Uniti si scambiano di più.",
    "cov.later": "Abbigliamento: in programma",
    "who1.h": "Se rivendi", "who1.p": "Vedi dove il prezzo si sta muovendo prima di comprare scorte, e controlli se il prezzo che ti viene offerto è in linea con il mercato.",
    "who2.h": "Se compri per te", "who2.p": "Capisci se stai pagando un prezzo alto o basso rispetto agli ultimi giorni, senza essere esperto di mercato.",
    "final.h": "Guarda cosa si muove oggi.",
    "foot1": "I prezzi sono stime di mercato in USD calcolate da dati StockX forniti tramite KicksDB, e possono differire dai prezzi reali al momento dell'acquisto. Hypewise non fornisce consulenza finanziaria.",
    "foot2": "Hypewise non è affiliato né sponsorizzato da StockX, Nike, Jordan, adidas o altri marchi citati. I nomi appartengono ai rispettivi proprietari.",
    "b.title": "Hypewise Prezzi",
    "b.sub": "Prezzi di mercato USA in dollari, solo scarpe verificate. Aggiornati ogni 1-2 giorni.",
    "b.demo": "DATI DI ESEMPIO. I prezzi mostrati sono esempi, non dati reali di mercato.",
    "b.search": "Cerca modello o SKU", "b.all": "Tutti", "b.brand": "Marchio", "b.sortlabel": "Ordina",
    "b.sort.move": "Maggiore variazione", "b.sort.price": "Prezzo più alto", "b.sort.name": "Nome",
    "b.nomatch": "Nessuna scarpa trovata con questi filtri.", "b.nodata": "Ancora nessun prezzo salvato. Vengono aggiunti a ogni aggiornamento.",
    "b.stat1": "Modelli seguiti", "b.stat2": "Marchi", "b.stat3": "Mosse oltre 5% in 7 giorni",
    "b.updated": "Aggiornato", "b.collecting": "in raccolta", "b.spark": "Andamento prezzo", "b.summary": "Riepilogo",
    "b.foot": "Prezzo medio di mercato in USD (fonte KicksDB / StockX). La variazione confronta l'ultimo prezzo con quello di circa 7 giorni prima; \"in raccolta\" significa che servono ancora almeno due rilevazioni."
  },
  ru: {
    "nav.how": "Как это работает", "nav.signal": "Сигнал", "nav.cover": "Что мы отслеживаем", "nav.open": "Открыть таблицу",
    "hero.eyebrow": "Цены перепродажи кроссовок, США",
    "hero.h1": "Покупай с <em>умом.</em>",
    "hero.lead": "Hypewise каждый день следит за ценами перепродажи самых востребованных кроссовок в США. Смотри, растёт ли цена, падает или стоит на месте, в долларах, не открывая десять разных сайтов.",
    "hero.cta2": "Как это работает",
    "card.tag": "Пример карточки", "card.tag2": "30 дней", "card.chg": "-4,2% за 7 дней", "card.v": "Жди",
    "card.vp": "Цена снижается уже 2 недели. Лучше подождать, пока она стабилизируется.",
    "card.fine": "Иллюстративный пример. Цены и график не являются реальными данными.",
    "how.h": "Как это работает", "how.intro": "Три шага, всё автоматически. Данные обновляются сами.",
    "s1.n": "ШАГ 1", "s1.h": "Собираем цены", "s1.p": "Мы считываем средние рыночные цены в долларах США по 50 самым востребованным моделям. Каждая модель обновляется раз в 1–2 дня.",
    "s2.n": "ШАГ 2", "s2.h": "Проверяем каждую карточку", "s2.p": "Мы отбрасываем результаты с неверной моделью или брендом, носки и аксессуары, устаревшие данные и нереалистичные цены. Оставляем только те пары, которым можно доверять.",
    "s3.n": "ШАГ 3", "s3.h": "Показываем динамику", "s3.p": "По каждой паре ты видишь сегодняшнюю цену, изменение за 7 дней и динамику во времени, чтобы с первого взгляда понять, что движется.",
    "sig.h": "Сигнал", "sig.soon": "скоро",
    "sig.intro": "По каждой паре Hypewise будет анализировать график и давать понятную подсказку, а ниже писать причину. Никаких случайных фраз: каждый сигнал объясняет, на чём он основан.",
    "cop.name": "Cop", "cop.p": "Цена близка к недавнему минимуму, и снижение замедляется. Возможно, подходящий момент для покупки.",
    "wait.name": "Жди", "wait.p": "Цена всё ещё падает, или сигналы противоречат друг другу. Лучше понаблюдать ещё несколько дней.",
    "sell.name": "Sell", "sell.p": "Цена близка к недавнему максимуму, и рост замедляется. Возможно, подходящий момент для продажи.",
    "sig.fine": "Это автоматические оценки на основе прошлых цен, призванные помочь тебе рассуждать. Они не являются финансовой рекомендацией, и их не следует воспринимать буквально. Если данных мало, Hypewise так и скажет, а не будет давать подсказку.",
    "cov.h": "Что мы отслеживаем", "cov.intro": "Пока мы сосредоточены на кроссовках, выбранных среди моделей, которыми больше всего торгуют в США.",
    "cov.later": "Одежда: в планах",
    "who1.h": "Если ты перепродаёшь", "who1.p": "Смотри, куда движутся цены, прежде чем закупать товар, и проверяй, соответствует ли предложенная тебе цена рынку.",
    "who2.h": "Если покупаешь для себя", "who2.p": "Понимай, высокую или низкую цену ты платишь по сравнению с последними днями, даже не будучи экспертом по рынку.",
    "final.h": "Смотри, что движется сегодня.",
    "foot1": "Цены являются рыночными оценками в долларах США, рассчитанными по данным StockX, полученным через KicksDB, и могут отличаться от реальных цен на момент покупки. Hypewise не предоставляет финансовых консультаций.",
    "foot2": "Hypewise не связан со StockX, Nike, Jordan, adidas и другими упомянутыми брендами и не спонсируется ими. Названия принадлежат их владельцам.",
    "b.title": "Hypewise Цены",
    "b.sub": "Цены американского рынка в долларах, только проверенные кроссовки. Обновляется раз в 1–2 дня.",
    "b.demo": "ПРИМЕР ДАННЫХ. Показанные цены являются примерами, а не реальными рыночными данными.",
    "b.search": "Поиск по модели или SKU", "b.all": "Все", "b.brand": "Бренд", "b.sortlabel": "Сортировка",
    "b.sort.move": "Наибольшее изменение", "b.sort.price": "Самая высокая цена", "b.sort.name": "Название",
    "b.nomatch": "Нет кроссовок, подходящих под эти фильтры.", "b.nodata": "Пока нет сохранённых цен. Они добавляются при каждом обновлении.",
    "b.stat1": "Отслеживаемые модели", "b.stat2": "Бренды", "b.stat3": "Изменения более 5% за 7 дней",
    "b.updated": "Обновлено", "b.collecting": "сбор данных", "b.spark": "Динамика цены", "b.summary": "Сводка",
    "b.foot": "Средняя рыночная цена в USD (источник: KicksDB / StockX). Изменение сравнивает последнюю цену с ценой примерно 7-дневной давности; «сбор данных» означает, что нужно ещё как минимум два замера."
  }
  };

  var lang = "en";
  function pick() {
    var saved = null;
    try { saved = localStorage.getItem("hw-lang"); } catch (e) {}
    if (saved && D[saved]) return saved;
    var nav = (navigator.language || "en").slice(0, 2).toLowerCase();
    return D[nav] ? nav : "en";
  }
  function t(key) { return (D[lang] && D[lang][key]) || D.en[key] || key; }
  function locale() { for (var i = 0; i < LANGS.length; i++) if (LANGS[i][0] === lang) return LANGS[i][2]; return "en-US"; }

  function apply() {
    document.documentElement.lang = lang;
    var q = function (sel, fn) { Array.prototype.forEach.call(document.querySelectorAll(sel), fn); };
    q("[data-i18n]", function (el) { el.textContent = t(el.getAttribute("data-i18n")); });
    q("[data-i18n-html]", function (el) { el.innerHTML = t(el.getAttribute("data-i18n-html")); });
    q("[data-i18n-ph]", function (el) { el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph"))); });
    q("[data-i18n-aria]", function (el) { el.setAttribute("aria-label", t(el.getAttribute("data-i18n-aria"))); });
    var title = document.querySelector("title");
    if (title && document.body.getAttribute("data-title")) title.textContent = t(document.body.getAttribute("data-title"));
    var sel = document.getElementById("lang");
    if (sel) sel.value = lang;
  }

  function set(code) {
    if (!D[code]) return;
    lang = code;
    try { localStorage.setItem("hw-lang", code); } catch (e) {}
    apply();
    document.dispatchEvent(new CustomEvent("hw-lang"));
  }

  function mount() {
    var sel = document.getElementById("lang");
    if (sel) {
      sel.innerHTML = LANGS.map(function (l) { return '<option value="' + l[0] + '">' + l[1] + "</option>"; }).join("");
      sel.addEventListener("change", function () { set(sel.value); });
    }
    lang = pick();
    apply();
  }

  function add(code, obj) { D[code] = Object.assign(D[code] || {}, obj); }
  function f(key, vars) { return t(key).replace(/\{(\w+)\}/g, function (m, k) { return vars && vars[k] != null ? vars[k] : m; }); }
  window.HW = { t: t, f: f, add: add, locale: locale, set: set, apply: apply, mount: mount, lang: function () { return lang; } };
})();
