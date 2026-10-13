// Telegram'a büyük dosya (<= 2 GB, tek parça) gönderir: bot olarak MTProto, WebSocket + TLS (wss) üzerinden.
// Neden WSS: bu ortamın çıkışı TLS'i yeniden sonlandıran bir HTTPS vekili; düz MTProto (TCP) geçmiyor.
// Gizli bilgiler YALNIZ ortamdan: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
// TG_SESSION_FILE (oturum dosyası, repo dışı). Kullanım (tools/telegram_gonder.py çağırır):
//   node gonder.js gonder <dosya> [açıklama]     |  node gonder.js yukle <dosya>  (mesajsız yükleme testi)
const fs = require('fs');
const path = require('path');
const { TelegramClient } = require('telegram');
const { StringSession } = require('telegram/sessions');
const { PromisedWebSockets } = require('telegram/extensions');
const { ConnectionTCPObfuscated } = require('telegram/network');
const { CustomFile } = require('telegram/client/uploads');
const { w3cwebsocket } = require('websocket');
const { HttpsProxyAgent } = require('https-proxy-agent');

const vekil = process.env.HTTPS_PROXY || process.env.https_proxy;
const agent = vekil ? new HttpsProxyAgent(vekil) : undefined;

function sunucu(ip) {  // veri merkezi IP'si -> web.telegram.org alan adı (TLS sertifikası için)
  if (/[a-z]/i.test(ip)) return ip;
  if (ip.startsWith('149.154.175.5')) return 'pluto.web.telegram.org';
  if (ip.startsWith('149.154.167.5') || ip.startsWith('149.154.167.4')) return 'venus.web.telegram.org';
  if (ip.startsWith('149.154.175.10')) return 'aurora.web.telegram.org';
  if (ip.startsWith('149.154.167.9')) return 'vesta.web.telegram.org';
  if (ip.startsWith('91.108.56.') || ip.startsWith('91.108.4.')) return 'flora.web.telegram.org';
  return 'venus.web.telegram.org';
}

class VekilWS extends PromisedWebSockets {
  getWebSocketLink(ip, port, test) { return `wss://${sunucu(ip)}:443/apiws${test ? '_test' : ''}`; }
  async connect(port, ip, testServers = false) {
    this.stream = Buffer.alloc(0);
    this.canRead = new Promise((r) => { this.resolveRead = r; });
    this.closed = false;
    this.website = this.getWebSocketLink(ip, port, testServers);
    this.client = new w3cwebsocket(this.website, 'binary', undefined, undefined, agent ? { agent } : undefined);
    return new Promise((resolve, reject) => {
      this.client.onopen = () => { this.receive(); resolve(this); };
      this.client.onerror = (e) => reject(e);
      this.client.onclose = () => { this.resolveRead(false); this.closed = true; };
    });
  }
}

function gizle(s) {
  let m = String(s);
  for (const k of ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_API_HASH']) if (process.env[k]) m = m.split(process.env[k]).join('***');
  return m;
}

async function istemci() {
  const yol = process.env.TG_SESSION_FILE;
  const sess = new StringSession(yol && fs.existsSync(yol) ? fs.readFileSync(yol, 'utf8').trim() : '');
  const c = new TelegramClient(sess, parseInt(process.env.TELEGRAM_API_ID, 10), process.env.TELEGRAM_API_HASH, {
    useWSS: true, networkSocket: VekilWS, connection: ConnectionTCPObfuscated, connectionRetries: 5,
  });
  c.setLogLevel('error');
  await c.start({ botAuthToken: process.env.TELEGRAM_BOT_TOKEN });
  if (yol) fs.writeFileSync(yol, c.session.save(), { mode: 0o600 });
  return c;
}

(async () => {
  const [komut, dosya, aciklama] = process.argv.slice(2);
  if (!['gonder', 'yukle'].includes(komut) || !dosya) {
    console.error('kullanım: node gonder.js gonder|yukle <dosya> [açıklama]');
    process.exit(2);
  }
  const boyut = fs.statSync(dosya).size;
  const c = await istemci();
  const t0 = Date.now();
  let son = -10;
  const ilerleme = (p) => { const y = Math.floor(p * 100); if (y >= son + 10) { son = y; console.log(`yükleniyor %${y}`); } };
  const cf = new CustomFile(path.basename(dosya), boyut, dosya);
  if (komut === 'yukle') {
    await c.uploadFile({ file: cf, workers: 4, onProgress: ilerleme });
  } else {
    await c.sendFile(parseInt(process.env.TELEGRAM_CHAT_ID, 10), {
      file: cf, caption: (aciklama || '').slice(0, 1000), forceDocument: true, workers: 4, progressCallback: ilerleme,
    });
  }
  console.log(`${komut === 'yukle' ? 'yüklendi (mesaj yok)' : 'gönderildi'}: ${path.basename(dosya)} ` +
              `${(boyut / 1e6).toFixed(1)} MB, ${((Date.now() - t0) / 1000).toFixed(0)} sn`);
  await c.disconnect();
  process.exit(0);
})().catch((e) => { console.error('HATA', gizle(e && e.message ? e.message : e)); process.exit(1); });
