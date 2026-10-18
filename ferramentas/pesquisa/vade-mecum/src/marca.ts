// Marca da Advocacia Aberta para o handshake do MCP.
//
// O ícone vai embutido como data URI (a spec aceita "URL or data URI" em Icon.src)
// em vez de apontar para uma URL. Assim ele não depende de o site estar no ar nem de
// haver um servidor de arquivos ao lado: o mesmo binário serve o ícone na VM, atrás do
// Caddy, e no cluster, onde o serviço é ClusterIP privado e não existe /var/www.
//
// O SVG fica como texto legível e a codificação é feita aqui — um blob base64 no
// fonte esconderia a marca de quem for editá-la.

const MARCA_CLARA = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Advocacia Aberta"><rect width="64" height="64" rx="14" fill="#FAFAF8"/><rect x="10" y="9" width="8" height="46" rx="3" fill="#2563EB"/><path d="M30 13h25v38H30" fill="none" stroke="#111111" stroke-width="6" stroke-linecap="square" stroke-linejoin="miter"/></svg>`;

// Variante para fundo escuro: mesma geometria, com o traço e o fundo invertidos e o
// azul um tom acima (#3B82F6), que mantém contraste sobre o fundo escuro.
const MARCA_ESCURA = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Advocacia Aberta"><rect width="64" height="64" rx="14" fill="#111111"/><rect x="10" y="9" width="8" height="46" rx="3" fill="#3B82F6"/><path d="M30 13h25v38H30" fill="none" stroke="#FAFAF8" stroke-width="6" stroke-linecap="square" stroke-linejoin="miter"/></svg>`;

function dataUri(svg: string): string {
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

export const ICONES_DA_MARCA = [
  {
    src: dataUri(MARCA_CLARA),
    mimeType: "image/svg+xml",
    sizes: ["any"],
    theme: "light" as const,
  },
  {
    src: dataUri(MARCA_ESCURA),
    mimeType: "image/svg+xml",
    sizes: ["any"],
    theme: "dark" as const,
  },
];
