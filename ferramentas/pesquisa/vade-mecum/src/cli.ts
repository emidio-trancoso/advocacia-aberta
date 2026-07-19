/**
 * CLI para uso direto (slash commands, scripts).
 * Uso: bun run src/cli.ts <tool> <args...>
 *
 * Exemplos:
 *   bun run src/cli.ts sumula "dano moral cadastro" STJ 5
 *   bun run src/cli.ts tese "plano de saude cobertura" 5
 *   bun run src/cli.ts tema "honorarios fazenda publica" 5
 *   bun run src/cli.ts tema-rg "ICMS base calculo PIS COFINS" 5
 *   bun run src/cli.ts informativo "principio da insignificancia" 5
 *   bun run src/cli.ts espelho "honorarios apreciacao equitativa" 5
 *   bun run src/cli.ts legislacao "186" CC 5
 *   bun run src/cli.ts buscar "responsabilidade civil dano" 5
 */

import { buscarSumulas, formatSumula, type Tribunal } from "./search/sumulas.js";
import { buscarTeses, formatTese } from "./search/jt.js";
import { buscarTemas, formatTema } from "./search/temas.js";
import { buscarTemasRG, formatTemaRG } from "./search/temas_rg_stf.js";
import { buscarInformativos, formatInformativo } from "./search/informativo_stf.js";
import { buscarEspelhos, formatEspelho } from "./search/espelhos_stj.js";
import {
  buscarLegislacao,
  CODIGOS_DISPONIVEIS,
  formatArtigo,
  normalizarCodigo,
} from "./search/legislacao.js";

const [, , tool, query, arg3, arg4] = process.argv;

function printSep() { console.log("\n" + "─".repeat(60) + "\n"); }

if (!tool || !query) {
  console.error("Uso: bun run src/cli.ts <sumula|tese|tema|tema-rg|informativo|espelho|legislacao|buscar> <query> [args]");
  process.exit(1);
}

switch (tool) {
  case "sumula": {
    const tribunal = (arg3 ?? "todos") as Tribunal | "todos";
    const limit = parseInt(arg4 ?? "5", 10);
    const results = buscarSumulas(query, tribunal, limit);
    if (results.length === 0) { console.log(`Nenhuma súmula encontrada para: "${query}"`); break; }
    console.log(`${results.length} súmula(s) encontrada(s)\n`);
    results.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatSumula(r)); });
    break;
  }

  case "tese": {
    const limit = parseInt(arg3 ?? "5", 10);
    const results = buscarTeses(query, limit);
    if (results.length === 0) { console.log(`Nenhuma tese encontrada para: "${query}"`); break; }
    console.log(`${results.length} tese(s) encontrada(s)\n`);
    results.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatTese(r)); });
    break;
  }

  case "tema": {
    const limit = parseInt(arg3 ?? "5", 10);
    const results = buscarTemas(query, limit);
    if (results.length === 0) { console.log(`Nenhum tema encontrado para: "${query}"`); break; }
    console.log(`${results.length} tema(s) encontrado(s)\n`);
    results.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatTema(r)); });
    break;
  }

  case "tema-rg": {
    const limit = parseInt(arg3 ?? "5", 10);
    const results = buscarTemasRG(query, limit);
    if (results.length === 0) { console.log(`Nenhum tema de repercussão geral encontrado para: "${query}"`); break; }
    console.log(`${results.length} tema(s) de repercussão geral encontrado(s)\n`);
    results.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatTemaRG(r)); });
    break;
  }

  case "informativo": {
    const limit = parseInt(arg3 ?? "5", 10);
    const results = buscarInformativos(query, limit);
    if (results.length === 0) { console.log(`Nenhum julgado do Informativo encontrado para: "${query}"`); break; }
    console.log(`${results.length} julgado(s) do Informativo encontrado(s)\n`);
    results.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatInformativo(r)); });
    break;
  }

  case "espelho": {
    const limit = parseInt(arg3 ?? "5", 10);
    const results = buscarEspelhos(query, limit);
    if (results.length === 0) { console.log(`Nenhum espelho de acórdão encontrado para: "${query}"`); break; }
    console.log(`${results.length} espelho(s) de acórdão encontrado(s)\n`);
    results.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatEspelho(r)); });
    break;
  }

  case "legislacao": {
    const codigoInformado = arg3 ?? "todos";
    const codigo = normalizarCodigo(codigoInformado);
    const limit = parseInt(arg4 ?? "5", 10);
    if (!codigo) {
      const disponiveis = [...CODIGOS_DISPONIVEIS, "todos"].join(", ");
      console.error(`Código de legislação indisponível: "${codigoInformado}". Use: ${disponiveis}.`);
      process.exitCode = 1;
      break;
    }
    const results = buscarLegislacao(query, codigo, limit);
    if (results.length === 0) { console.log(`Nenhum artigo encontrado para: "${query}"`); break; }
    console.log(`${results.length} artigo(s) encontrado(s)\n`);
    results.forEach(({ codigo: cod, artigo }, i) => { if (i > 0) printSep(); process.stdout.write(formatArtigo(cod, artigo)); });
    break;
  }

  case "buscar": {
    // Busca ampla: súmulas + teses + temas repetitivos + temas de RG + Informativo STF
    const limit = parseInt(arg3 ?? "3", 10);

    const sumulas = buscarSumulas(query, "todos", limit);
    const teses = buscarTeses(query, limit);
    const temas = buscarTemas(query, limit);
    const temasRG = buscarTemasRG(query, limit);
    const informativos = buscarInformativos(query, limit);
    const espelhos = buscarEspelhos(query, limit);

    const total = sumulas.length + teses.length + temas.length + temasRG.length + informativos.length + espelhos.length;
    if (total === 0) { console.log(`Nenhum resultado encontrado para: "${query}"`); break; }

    console.log(`=== BASE JURÍDICA LOCAL — "${query}" ===\n`);

    if (sumulas.length > 0) {
      console.log(`## SÚMULAS (${sumulas.length})\n`);
      sumulas.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatSumula(r)); });
    }
    if (teses.length > 0) {
      printSep();
      console.log(`## JURISPRUDÊNCIA EM TESES (${teses.length})\n`);
      teses.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatTese(r)); });
    }
    if (temas.length > 0) {
      printSep();
      console.log(`## TEMAS REPETITIVOS (${temas.length})\n`);
      temas.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatTema(r)); });
    }
    if (temasRG.length > 0) {
      printSep();
      console.log(`## TEMAS DE REPERCUSSÃO GERAL STF (${temasRG.length})\n`);
      temasRG.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatTemaRG(r)); });
    }
    if (informativos.length > 0) {
      printSep();
      console.log(`## INFORMATIVO STF (${informativos.length})\n`);
      informativos.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatInformativo(r)); });
    }
    if (espelhos.length > 0) {
      printSep();
      console.log(`## ESPELHOS DE ACÓRDÃOS STJ (${espelhos.length})\n`);
      espelhos.forEach((r, i) => { if (i > 0) printSep(); process.stdout.write(formatEspelho(r)); });
    }
    break;
  }

  default:
    console.error(`Tool desconhecida: ${tool}. Use: sumula | tese | tema | tema-rg | informativo | espelho | legislacao | buscar`);
    process.exit(1);
}
