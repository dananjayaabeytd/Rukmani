/**
 * Interface text in English, Sinhala and Tamil.
 *
 * Every visible string in the UI comes from here, so switching language
 * changes the whole interface. Rukmani's own replies follow the language
 * the customer writes in; the messages that buttons send (e.g. "Add to
 * cart") are in the chosen language too, so she answers in it.
 *
 * To add a string: add it to the `Strings` type, then to all three objects
 * (TypeScript will point out any language that's missing it).
 */

export type Lang = "en" | "si" | "ta";

export const LANGUAGES: { code: Lang; label: string }[] = [
  { code: "en", label: "EN" },
  { code: "si", label: "සිං" },
  { code: "ta", label: "தமிழ்" },
];

/** What Rukmani is doing, shown in the status pill. */
type StatusKey =
  | "thinking"
  | "search"
  | "details"
  | "city"
  | "delivery"
  | "cart"
  | "checkout"
  | "tracking"
  | "abroad"
  | "working";

/** Which status each backend tool shows. */
const TOOL_STATUS: Record<string, StatusKey> = {
  search_products: "search",
  get_product_details: "details",
  find_delivery_city: "city",
  check_delivery: "delivery",
  add_to_cart: "cart",
  update_cart_item: "cart",
  remove_from_cart: "cart",
  prepare_checkout: "checkout",
  track_order: "tracking",
  list_gift_countries: "abroad",
  browse_gift_store: "abroad",
};

export function statusKeyFor(tool: string): StatusKey {
  return TOOL_STATUS[tool] ?? "working";
}

export interface Strings {
  locale: string; // for dates, e.g. "si-LK"
  name: string;
  tagline: string;
  newChat: string;
  cartLabel: (count: number) => string;
  welcomeTitle: string;
  welcomeLanguages: string;
  welcomeIntro: string;
  suggestions: string[];
  occasionSoon: (name: string, days: number) => string;
  occasionToday: (name: string) => string;
  occasionCta: (name: string) => string;
  occasionMessage: (name: string) => string;
  placeholder: string;
  messageLabel: string;
  send: string;
  status: Record<StatusKey, string>;
  connectionError: string;
  // product cards
  addToCart: string;
  viewOnKapruka: string;
  openOnKapruka: string;
  sale: string;
  islandWide: string;
  limitedCities: (count: number | string) => string;
  // delivery
  deliveryTo: (city: string) => string;
  canArrive: string;
  dateFull: (date: string) => string;
  earliest: string;
  deliveryFee: string;
  upTo: string;
  notDelivered: (city: string) => string;
  canGoTo: string;
  andMore: string;
  pickDate: string;
  // cart
  yourCart: string;
  cartEmpty: string;
  drawerEmpty: string;
  itemsTotal: string;
  checkout: string;
  checkoutWithRukmani: string;
  icing: string;
  remove: (name: string) => string;
  closeCart: string;
  // checkout
  checkYourOrder: string;
  items: string;
  delivery: string;
  total: string;
  confirm: string;
  placing: string;
  outdated: string;
  dear: (name: string) => string;
  anonymous: string;
  economyDelivery: string;
  deliveredAbroad: (country: string) => string;
  // payment
  orderReady: (ref: string) => string;
  deliveryOn: string;
  payNote: string;
  payNow: (amount: string) => string;
  priceHeld: (minutes: number) => string;
  linkExpired: string;
  // tracking
  orderNumber: (number: string) => string;
  forRecipient: (name: string, city: string | null) => string;
  deliveryLabel: string;
  toBeConfirmed: string;
  delivered: string;
  cancelled: string;
  // messages that buttons send to Rukmani
  msgAdd: (name: string, id: string) => string;
  msgRemove: (name: string, id: string) => string;
  msgCheckout: string;
  msgCheckDate: (city: string, date: string, productId: string | null) => string;
}

const en: Strings = {
  locale: "en-GB",
  name: "Rukmani",
  tagline: "Your gift concierge",
  newChat: "New chat",
  cartLabel: (n) => `Cart, ${n} items`,
  welcomeTitle: "Ayubowan! I'm Rukmani",
  welcomeLanguages: "ආයුබෝවන් · வணக்கம் · Hello",
  welcomeIntro:
    "Tell me who the gift is for, the occasion and when it should arrive. Ask in Sinhala, Tamil, Singlish, Tanglish or English, and I'll find something lovely on Kapruka.",
  suggestions: [
    "A birthday cake for my mother",
    "Valentine's roses for my wife",
    "Can you deliver a chocolate hamper to Kandy tomorrow?",
    "A get-well-soon gift under LKR 5,000",
  ],
  occasionSoon: (name, d) => `${name} is in ${d} day${d === 1 ? "" : "s"}`,
  occasionToday: (name) => `${name} is today!`,
  occasionCta: (name) => `Find a ${name} gift`,
  occasionMessage: (name) => `Help me find a ${name} gift`,
  placeholder: "Ask in Sinhala, Tamil or English…",
  messageLabel: "Message Rukmani",
  send: "Send",
  status: {
    thinking: "Thinking",
    search: "Searching Kapruka for gifts",
    details: "Looking at the product details",
    city: "Finding the delivery city",
    delivery: "Checking delivery date and fee",
    cart: "Updating your cart",
    checkout: "Preparing your checkout",
    tracking: "Tracking your order",
    abroad: "Browsing Kapruka's overseas gift stores",
    working: "Working on it",
  },
  connectionError: "I can't reach the shop right now. Please check your connection and try again.",
  addToCart: "Add to cart",
  viewOnKapruka: "View on Kapruka",
  openOnKapruka: "Open on Kapruka",
  sale: "Sale",
  islandWide: "Delivered island-wide",
  limitedCities: (n) => `Delivered to ${n} cities only`,
  deliveryTo: (city) => `Delivery to ${city}`,
  canArrive: "Can arrive on",
  dateFull: (date) => `${date} is full.`,
  earliest: "Earliest:",
  deliveryFee: "Delivery fee:",
  upTo: "Up to ",
  notDelivered: (city) => `This item isn't delivered to ${city}.`,
  canGoTo: "It can go to:",
  andMore: " and more",
  pickDate: "Pick a delivery date",
  yourCart: "Your cart",
  cartEmpty: "Your cart is empty.",
  drawerEmpty: "Nothing here yet. Ask Rukmani for gift ideas!",
  itemsTotal: "Items total",
  checkout: "Checkout",
  checkoutWithRukmani: "Checkout with Rukmani",
  icing: "Icing",
  remove: (name) => `Remove ${name}`,
  closeCart: "Close cart",
  checkYourOrder: "Check your order",
  items: "Items",
  delivery: "Delivery",
  total: "Total",
  confirm: "Confirm & get payment link",
  placing: "Placing your order…",
  outdated: "This summary was updated — see the newest one below.",
  dear: (name) => `Dear ${name},`,
  anonymous: "Anonymous",
  economyDelivery: "Economy delivery",
  deliveredAbroad: (country) => `Delivered in ${country} by Kapruka's partner`,
  orderReady: (ref) => `Order ready · ${ref}`,
  deliveryOn: "Delivery on",
  payNote: "Pay on Kapruka's secure page to complete it — no account needed.",
  payNow: (amount) => `Pay ${amount} now`,
  priceHeld: (m) => `Price held for ${m} more minute${m === 1 ? "" : "s"}`,
  linkExpired: "This link has expired. Ask Rukmani to prepare the checkout again.",
  orderNumber: (n) => `Order ${n}`,
  forRecipient: (name, city) => `For ${name}${city ? ` in ${city}` : ""}`,
  deliveryLabel: "Delivery:",
  toBeConfirmed: "to be confirmed",
  delivered: "Delivered — thank you for shopping with Kapruka!",
  cancelled: "This order was cancelled.",
  msgAdd: (name, id) => `Add "${name}" (${id}) to my cart`,
  msgRemove: (name, id) => `Remove "${name}" (${id}) from my cart`,
  msgCheckout: "I'm ready to check out",
  msgCheckDate: (city, date, id) => `Can you deliver to ${city} on ${date}${id ? ` (${id})` : ""}?`,
};

const si: Strings = {
  locale: "si-LK",
  name: "රුක්මණී",
  tagline: "ඔබේ තෑගි උපදේශිකාව",
  newChat: "අලුත් කතාබහක්",
  cartLabel: (n) => `කරත්තය, භාණ්ඩ ${n}`,
  welcomeTitle: "ආයුබෝවන්! මම රුක්මණී",
  welcomeLanguages: "Ayubowan · வணக்கம் · Hello",
  welcomeIntro:
    "තෑග්ග කාටද, මොන අවස්ථාවටද, කවදා ලැබෙන්න ඕනෙද කියන්න. සිංහලෙන්, Singlish වලින්, දෙමළෙන් හෝ ඉංග්‍රීසියෙන් අහන්න — මම Kapruka එකෙන් ලස්සන දෙයක් හොයලා දෙන්නම්.",
  suggestions: [
    "අම්මට birthday cake එකක් ඕනේ",
    "බිරිඳට Valentine's රෝස මල් ටිකක්",
    "Kandy walata heta chocolate hamper ekak yawanna puluwanda?",
    "ඉක්මනින් සුව වේවා කියලා දෙන්න රු. 5,000 ට අඩු තෑග්ගක්",
  ],
  occasionSoon: (name, d) => `${name}ට තව දින ${d}යි`,
  occasionToday: (name) => `අද ${name}!`,
  occasionCta: (name) => `${name} තෑග්ගක් හොයමු`,
  occasionMessage: (name) => `${name} තෑග්ගක් හොයන්න උදව් කරන්න`,
  placeholder: "සිංහල, Singlish, தமிழ் හෝ English වලින් අහන්න…",
  messageLabel: "රුක්මණීට පණිවිඩයක්",
  send: "යවන්න",
  status: {
    thinking: "හිතමින්",
    search: "Kapruka එකේ තෑගි හොයමින්",
    details: "භාණ්ඩයේ විස්තර බලමින්",
    city: "නගරය හොයමින්",
    delivery: "බෙදාහැරීමේ දිනය සහ ගාස්තුව බලමින්",
    cart: "කරත්තය යාවත්කාලීන කරමින්",
    checkout: "Checkout එක සකස් කරමින්",
    tracking: "ඇණවුම සොයමින්",
    abroad: "විදෙස් තෑගි වෙළඳසැල් බලමින්",
    working: "වැඩේ කරමින්",
  },
  connectionError:
    "දැනට සාප්පුවට සම්බන්ධ වෙන්න බැහැ. ඔබේ සම්බන්ධතාවය පරීක්ෂා කර නැවත උත්සාහ කරන්න.",
  addToCart: "කරත්තයට දාන්න",
  viewOnKapruka: "Kapruka එකේ බලන්න",
  openOnKapruka: "Kapruka එකේ විවෘත කරන්න",
  sale: "වට්ටම්",
  islandWide: "දිවයින පුරා බෙදාහරිනවා",
  limitedCities: (n) => `තෝරාගත් නගර ${n} කට පමණයි`,
  deliveryTo: (city) => `${city} වෙත බෙදාහැරීම`,
  canArrive: "ලැබිය හැකි දිනය:",
  dateFull: (date) => `${date} දිනය පිරිලා.`,
  earliest: "ඉක්මනින්ම:",
  deliveryFee: "බෙදාහැරීමේ ගාස්තුව:",
  upTo: "උපරිම ",
  notDelivered: (city) => `මේ භාණ්ඩය ${city} වෙත යවන්න බැහැ.`,
  canGoTo: "යැවිය හැකි නගර:",
  andMore: " සහ තවත්",
  pickDate: "බෙදාහැරීමේ දිනයක් තෝරන්න",
  yourCart: "ඔබේ කරත්තය",
  cartEmpty: "ඔබේ කරත්තය හිස්.",
  drawerEmpty: "තවම මොකුත් නැහැ. තෑගි අදහස් රුක්මණීගෙන් අහන්න!",
  itemsTotal: "භාණ්ඩ එකතුව",
  checkout: "Checkout",
  checkoutWithRukmani: "රුක්මණී සමඟ checkout කරන්න",
  icing: "අයිසිං",
  remove: (name) => `${name} ඉවත් කරන්න`,
  closeCart: "කරත්තය වසන්න",
  checkYourOrder: "ඔබේ ඇණවුම පරීක්ෂා කරන්න",
  items: "භාණ්ඩ",
  delivery: "බෙදාහැරීම",
  total: "මුළු මුදල",
  confirm: "තහවුරු කර ගෙවීම් link එක ගන්න",
  placing: "ඇණවුම සකස් කරමින්…",
  outdated: "මේ සාරාංශය යාවත්කාලීන වුණා — පහළ අලුත් එක බලන්න.",
  dear: (name) => `ආදරණීය ${name},`,
  anonymous: "නම නොකියා",
  economyDelivery: "අඩු මිල බෙදාහැරීම",
  deliveredAbroad: (country) => `${country} තුළ Kapruka හවුල්කරු විසින් බෙදාහරී`,
  orderReady: (ref) => `ඇණවුම සූදානම් · ${ref}`,
  deliveryOn: "බෙදාහැරීම:",
  payNote: "ඇණවුම සම්පූර්ණ කරන්න Kapruka හි ආරක්ෂිත පිටුවෙන් ගෙවන්න — ගිණුමක් අවශ්‍ය නැහැ.",
  payNow: (amount) => `${amount} දැන් ගෙවන්න`,
  priceHeld: (m) => `මිල තව මිනිත්තු ${m}ක් රඳවා තබයි`,
  linkExpired: "මේ link එක කල් ඉකුත් වුණා. Checkout එක නැවත සකස් කරන්න රුක්මණීගෙන් ඉල්ලන්න.",
  orderNumber: (n) => `ඇණවුම ${n}`,
  forRecipient: (name, city) => `${name}${city ? `, ${city}` : ""} සඳහා`,
  deliveryLabel: "බෙදාහැරීම:",
  toBeConfirmed: "තවම තහවුරු නැහැ",
  delivered: "බෙදාහැරියා — Kapruka සමඟ සාප්පු සවාරි කළාට ස්තූතියි!",
  cancelled: "මේ ඇණවුම අවලංගු කළා.",
  msgAdd: (name, id) => `"${name}" (${id}) කරත්තයට දාන්න`,
  msgRemove: (name, id) => `"${name}" (${id}) කරත්තයෙන් අයින් කරන්න`,
  msgCheckout: "මම checkout කරන්න ලෑස්තියි",
  msgCheckDate: (city, date, id) =>
    `${date} දින ${city} වෙත යවන්න පුළුවන්ද${id ? ` (${id})` : ""}?`,
};

const ta: Strings = {
  locale: "ta-LK",
  name: "ருக்மணி",
  tagline: "உங்கள் பரிசு ஆலோசகர்",
  newChat: "புதிய உரையாடல்",
  cartLabel: (n) => `கூடை, ${n} பொருட்கள்`,
  welcomeTitle: "வணக்கம்! நான் ருக்மணி",
  welcomeLanguages: "Hello · ආයුබෝවන් · வணக்கம்",
  welcomeIntro:
    "பரிசு யாருக்கு, என்ன நிகழ்வு, எப்போது சேர வேண்டும் என்று சொல்லுங்கள். தமிழ், Tanglish, சிங்களம் அல்லது ஆங்கிலத்தில் கேளுங்கள் — Kapruka-வில் அழகான ஒன்றைத் தேடித் தருகிறேன்.",
  suggestions: [
    "அம்மாவுக்கு ஒரு birthday cake வேண்டும்",
    "Amma ku birthday cake venum, budget 7000",
    "நாளை கண்டிக்கு chocolate hamper அனுப்ப முடியுமா?",
    "Valentine's day ku wife ku roses anupanum",
  ],
  occasionSoon: (name, d) => `${name}க்கு இன்னும் ${d} நாட்கள்`,
  occasionToday: (name) => `இன்று ${name}!`,
  occasionCta: (name) => `${name} பரிசு தேடலாம்`,
  occasionMessage: (name) => `${name} பரிசு தேட உதவுங்கள்`,
  placeholder: "தமிழ், Tanglish, සිංහල அல்லது English-ல் கேளுங்கள்…",
  messageLabel: "ருக்மணிக்கு செய்தி",
  send: "அனுப்பு",
  status: {
    thinking: "யோசிக்கிறேன்",
    search: "Kapruka-வில் பரிசுகளைத் தேடுகிறேன்",
    details: "பொருளின் விவரங்களைப் பார்க்கிறேன்",
    city: "நகரத்தைத் தேடுகிறேன்",
    delivery: "டெலிவரி நாள் மற்றும் கட்டணம் பார்க்கிறேன்",
    cart: "கூடையைப் புதுப்பிக்கிறேன்",
    checkout: "Checkout தயார் செய்கிறேன்",
    tracking: "ஆர்டரைக் கண்காணிக்கிறேன்",
    abroad: "வெளிநாட்டு பரிசுக் கடைகளைப் பார்க்கிறேன்",
    working: "செய்கிறேன்",
  },
  connectionError:
    "இப்போது கடையை அணுக முடியவில்லை. உங்கள் இணைப்பைச் சரிபார்த்து மீண்டும் முயற்சிக்கவும்.",
  addToCart: "கூடையில் சேர்",
  viewOnKapruka: "Kapruka-வில் பார்க்க",
  openOnKapruka: "Kapruka-வில் திறக்க",
  sale: "தள்ளுபடி",
  islandWide: "நாடு முழுவதும் டெலிவரி",
  limitedCities: (n) => `${n} நகரங்களுக்கு மட்டும் டெலிவரி`,
  deliveryTo: (city) => `${city}-க்கு டெலிவரி`,
  canArrive: "சேரக்கூடிய நாள்:",
  dateFull: (date) => `${date} நிரம்பிவிட்டது.`,
  earliest: "முதல் கிடைக்கும் நாள்:",
  deliveryFee: "டெலிவரி கட்டணம்:",
  upTo: "அதிகபட்சம் ",
  notDelivered: (city) => `இந்தப் பொருள் ${city}-க்கு அனுப்பப்படாது.`,
  canGoTo: "அனுப்பக்கூடிய இடங்கள்:",
  andMore: " மற்றும் பல",
  pickDate: "டெலிவரி நாளைத் தேர்வுசெய்க",
  yourCart: "உங்கள் கூடை",
  cartEmpty: "உங்கள் கூடை காலியாக உள்ளது.",
  drawerEmpty: "இன்னும் எதுவும் இல்லை. பரிசு யோசனைகளை ருக்மணியிடம் கேளுங்கள்!",
  itemsTotal: "பொருட்களின் மொத்தம்",
  checkout: "Checkout",
  checkoutWithRukmani: "ருக்மணியுடன் checkout",
  icing: "ஐசிங்",
  remove: (name) => `${name}-ஐ நீக்கு`,
  closeCart: "கூடையை மூடு",
  checkYourOrder: "உங்கள் ஆர்டரைச் சரிபாருங்கள்",
  items: "பொருட்கள்",
  delivery: "டெலிவரி",
  total: "மொத்தம்",
  confirm: "உறுதிசெய்து பணம் செலுத்தும் link பெறுக",
  placing: "ஆர்டர் செய்யப்படுகிறது…",
  outdated: "இந்தச் சுருக்கம் புதுப்பிக்கப்பட்டது — கீழே உள்ள புதியதைப் பாருங்கள்.",
  dear: (name) => `அன்புள்ள ${name},`,
  anonymous: "பெயர் குறிப்பிடாமல்",
  economyDelivery: "குறைந்த கட்டண டெலிவரி",
  deliveredAbroad: (country) => `${country}-இல் Kapruka கூட்டாளர் டெலிவரி செய்வார்`,
  orderReady: (ref) => `ஆர்டர் தயார் · ${ref}`,
  deliveryOn: "டெலிவரி:",
  payNote: "ஆர்டரை முடிக்க Kapruka-வின் பாதுகாப்பான பக்கத்தில் பணம் செலுத்துங்கள் — கணக்கு தேவையில்லை.",
  payNow: (amount) => `${amount} இப்போது செலுத்துங்கள்`,
  priceHeld: (m) => `விலை இன்னும் ${m} நிமிடங்கள் நிலைத்திருக்கும்`,
  linkExpired: "இந்த link காலாவதியாகிவிட்டது. Checkout-ஐ மீண்டும் தயார் செய்ய ருக்மணியிடம் கேளுங்கள்.",
  orderNumber: (n) => `ஆர்டர் ${n}`,
  forRecipient: (name, city) => `${name}${city ? `, ${city}` : ""}-க்கு`,
  deliveryLabel: "டெலிவரி:",
  toBeConfirmed: "இன்னும் உறுதிசெய்யப்படவில்லை",
  delivered: "டெலிவரி செய்யப்பட்டது — Kapruka-வில் வாங்கியதற்கு நன்றி!",
  cancelled: "இந்த ஆர்டர் ரத்து செய்யப்பட்டது.",
  msgAdd: (name, id) => `"${name}" (${id}) கூடையில் சேர்க்கவும்`,
  msgRemove: (name, id) => `"${name}" (${id}) கூடையிலிருந்து நீக்கவும்`,
  msgCheckout: "நான் checkout செய்யத் தயார்",
  msgCheckDate: (city, date, id) =>
    `${date} அன்று ${city}-க்கு அனுப்ப முடியுமா${id ? ` (${id})` : ""}?`,
};

export const STRINGS: Record<Lang, Strings> = { en, si, ta };
