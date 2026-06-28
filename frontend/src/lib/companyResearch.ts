import type {
  CalculationResult,
  CompanyResearchBundle,
  CompanyResearchResponse,
  NormalizedFact,
  ResearchStandardSection,
  ScorecardItem,
  SupplyChainBottleneck
} from "./researchTypes";
import {
  aiCompanyMetadata,
  companyNameAliases,
  supportedFallbackTickers
} from "./aiCompanyCatalog";
import type { AiCompanyMetadata } from "./aiCompanyCatalog";

export type { CompanyResearchBundle, CompanyResearchResponse } from "./researchTypes";
export { supportedFallbackTickers } from "./aiCompanyCatalog";

const apiBaseUrl = () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function fetchCompanyResearch(ticker: string): Promise<CompanyResearchBundle> {
  const normalizedTicker = normalizeTicker(ticker);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/research/company/${normalizedTicker}`, {
      cache: "no-store",
      signal: controller.signal
    });
  } finally {
    clearTimeout(timeout);
  }
  if (!response.ok) {
    let detail = `Research request failed with status ${response.status}`;
    try {
      const errorPayload = (await response.json()) as { detail?: string };
      detail = errorPayload.detail ?? detail;
    } catch {
      // Keep the HTTP status message when the backend does not return JSON.
    }
    throw new Error(detail);
  }
  return { source: "api", report: (await response.json()) as CompanyResearchResponse };
}

type FallbackCompanyProfile = {
  ticker: string;
  name: string;
  cik: string;
  exchange?: string;
  industry?: string;
  description?: string;
  aiCategories?: string[];
  aiRelevanceScore?: number;
  aiReason?: string;
  sic: string;
  sicDescription: string;
  archetype: string;
  facts: {
    revenues: number;
    grossProfit: number;
    operatingIncome: number;
    netIncome: number;
    freeCashFlow: number;
  };
  metrics: {
    revenueGrowth: string;
    grossMargin: string;
    operatingMargin: string;
    netMargin: string;
    fcfMargin: string;
  };
  scenarioGrowth: {
    bear: number;
    base: number;
    bull: number;
  };
  thesis: string;
  recommendation: string;
  businessModel: string[];
  moat: string[];
  industryPosition: string[];
  valuationRead: string[];
  upgradeConditions: string[];
  downgradeConditions: string[];
  risks: string[];
  openQuestions: string[];
};

const fallbackProfiles: Record<string, FallbackCompanyProfile> = {
  AAPL: {
    ticker: "AAPL",
    name: "Apple Inc.",
    cik: "0000320193",
    sic: "3571",
    sicDescription: "Electronic Computers",
    archetype: "Consumer Goods",
    facts: {
      revenues: 391035000000,
      grossProfit: 181000000000,
      operatingIncome: 123216000000,
      netIncome: 93736000000,
      freeCashFlow: 106254000000
    },
    metrics: {
      revenueGrowth: "0.0202",
      grossMargin: "0.4629",
      operatingMargin: "0.3151",
      netMargin: "0.2397",
      fcfMargin: "0.2717"
    },
    scenarioGrowth: { bear: 0, base: 0.03, bull: 0.06 },
    thesis: "Apple 的研究重点是硬件换机周期、服务收入韧性、毛利结构和资本回报质量。",
    recommendation: "研究建议：纳入高质量现金流公司观察池，核心判断取决于服务收入韧性、硬件换机周期和估值安全边际。",
    businessModel: [
      "硬件销售提供用户入口，服务收入和生态粘性提升复购与利润稳定性。",
      "关键不是单年 iPhone 增长，而是装机基础、服务 ARPU、毛利结构和回购效率。",
      "需要把管理层对新品和 AI 功能的表述与真实收入、毛利和现金流变化分开验证。"
    ],
    moat: [
      "品牌、操作系统生态、开发者网络和高切换成本共同形成用户留存。",
      "供应链规模和渠道控制力有助于维持现金转换周期。",
      "护城河的反证是服务监管、硬件创新放缓和用户换机周期拉长。"
    ],
    industryPosition: [
      "属于消费电子与软件服务混合型公司，不能只按硬件制造估值。",
      "同业比较应同时看硬件毛利、服务毛利、用户规模、回购和净现金。"
    ],
    valuationRead: [
      "更适合以所有者收益、FCF yield、PE 和服务业务质量交叉验证。",
      "当收入低增长时，估值主要由利润率稳定性、回购收益率和服务增长支撑。"
    ],
    upgradeConditions: [
      "服务收入保持高质量增长且监管影响可控。",
      "硬件换机周期恢复，同时自由现金流率不被促销或供应链成本侵蚀。"
    ],
    downgradeConditions: [
      "服务业务增长明显放缓或受监管重塑收费模式。",
      "硬件销量疲弱叠加毛利率下行，导致回购无法抵消每股现金流压力。"
    ],
    risks: [
      "硬件需求对换机周期和宏观消费环境敏感。",
      "服务业务监管压力可能影响长期利润率假设。",
      "估值输出对低增长环境下的回购和服务增长假设敏感。"
    ],
    openQuestions: [
      "继续验证 iPhone 周期、服务收入和区域结构披露。",
      "接入市场价格后补充 PE、PS、EV/FCF 等交易倍数。"
    ]
  },
  NVDA: {
    ticker: "NVDA",
    name: "NVIDIA Corporation",
    cik: "0001045810",
    sic: "3674",
    sicDescription: "Semiconductors and Related Devices",
    archetype: "Semiconductor",
    facts: {
      revenues: 60900000000,
      grossProfit: 45675000000,
      operatingIncome: 32900000000,
      netIncome: 29760000000,
      freeCashFlow: 29430000000
    },
    metrics: {
      revenueGrowth: "0.4118",
      grossMargin: "0.7500",
      operatingMargin: "0.5402",
      netMargin: "0.4887",
      fcfMargin: "0.4833"
    },
    scenarioGrowth: { bear: 0.05, base: 0.16, bull: 0.26 },
    thesis: "Nvidia 的研究重点是 AI 加速器需求可持续性、数据中心收入质量、毛利率周期和客户集中度。",
    recommendation: "研究建议：列为高优先级科技产业核心跟踪对象，但在没有实时价格和最新 filing 验证前，不给出建仓结论；核心判断是“强基本面、高敏感估值、需持续验证订单质量”。",
    businessModel: [
      "Nvidia 不只是芯片公司，而是加速计算平台公司：GPU、网络、软件栈、开发者生态和系统方案共同决定客户粘性。",
      "数据中心增长质量要拆成训练需求、推理需求、云厂商资本开支、企业 AI 渗透和主权 AI 五类来源，不能只看总收入增速。",
      "自由现金流质量比 GAAP 净利润更重要：如果库存、预付款、先进封装供应约束或客户账期变化恶化，收入质量要降权。"
    ],
    moat: [
      "CUDA 软件生态、开发者习惯、系统级交付能力和领先产品节奏构成主要护城河。",
      "护城河不是永久事实，需要用毛利率、客户留存、软件附着率、产品代际性能和供给约束缓解情况复核。",
      "如果客户自研芯片明显替代通用 GPU，或开源/替代软件栈降低切换成本，护城河假设必须下调。"
    ],
    industryPosition: [
      "Nvidia 位于 AI 算力产业链的高价值环节，上游受先进制程、HBM、CoWoS/先进封装约束，下游受云厂商和大模型资本开支周期驱动。",
      "同业比较不能只看半导体 PE，应同时比较数据中心收入增速、毛利率、软件生态、客户集中度和供应链瓶颈。",
      "科技产业研究要把“技术领先”转化为“商业结果”：订单持续性、可交付产能、客户 ROI 和单位经济性。"
    ],
    valuationRead: [
      "DCF 适合检验长期自由现金流假设，EV/Sales 适合高增长阶段压力测试，PE 用于与成熟高利润科技公司横向比较。",
      "估值最敏感的不是第一年收入，而是三年后毛利率是否正常化、资本开支周期是否消化、以及终值增长是否合理。",
      "在没有实时股价时只能给研究结论，不能给目标价或实际上涨空间。"
    ],
    upgradeConditions: [
      "最新 filing 和管理层披露能证明数据中心增长来自更分散客户和真实推理/企业需求，而不只是少数云厂商集中采购。",
      "毛利率在供应放量后仍明显高于传统半导体周期水平，且自由现金流转换率保持强劲。",
      "客户自研 ASIC 没有显著压缩 Nvidia 的定价权或软件生态锁定。"
    ],
    downgradeConditions: [
      "云厂商资本开支增速放缓但 Nvidia 收入仍按高增长估值，导致增长假设和估值脱节。",
      "毛利率连续下行、库存或渠道信号转弱、或大客户集中度上升。",
      "出口限制、先进封装/HBM 供应、竞争产品或客户自研芯片改变未来三年现金流路径。"
    ],
    risks: [
      "AI 资本开支消化可能导致订单节奏波动。",
      "高毛利率可能随供应扩张和竞争加剧而正常化。",
      "大客户集中、出口管制和先进封装供应链需要持续审计。"
    ],
    openQuestions: [
      "验证最新 filing 中客户集中度和区域收入披露。",
      "跟踪云厂商资本开支、GPU 交付周期和毛利率指引变化。"
    ]
  },
  MSFT: {
    ticker: "MSFT",
    name: "Microsoft Corporation",
    cik: "0000789019",
    sic: "7372",
    sicDescription: "Services-Prepackaged Software",
    archetype: "SaaS / Software",
    facts: {
      revenues: 245000000000,
      grossProfit: 171500000000,
      operatingIncome: 109000000000,
      netIncome: 88100000000,
      freeCashFlow: 74000000000
    },
    metrics: {
      revenueGrowth: "0.1350",
      grossMargin: "0.7000",
      operatingMargin: "0.4449",
      netMargin: "0.3596",
      fcfMargin: "0.3020"
    },
    scenarioGrowth: { bear: 0.06, base: 0.11, bull: 0.15 },
    thesis: "Microsoft 的研究重点是云业务增长、AI Copilot 变现、资本开支效率和企业软件续费韧性。",
    recommendation: "研究建议：作为高质量企业软件与云平台核心样本持续跟踪，重点验证 AI 投入能否转化为可见收入和自由现金流。",
    businessModel: [
      "企业软件订阅、Azure 云、Office/Teams/GitHub/LinkedIn 形成多入口企业生态。",
      "看点不是单一产品发布，而是 AI 功能能否提高 ARPU、续费率和云消耗。",
      "资本开支需要和未来云收入、折旧压力和 FCF 转换率一起看。"
    ],
    moat: [
      "企业客户切换成本、开发者生态、渠道关系和混合云能力是核心护城河。",
      "监管与捆绑销售审查是护城河的主要反证。"
    ],
    industryPosition: [
      "处于企业软件、云基础设施和 AI 应用层交叉位置。",
      "同业比较应关注 Azure 增长、AI capex 回收期、营业利润率和 FCF。"
    ],
    valuationRead: [
      "适合 PE、EV/FCF、SOTP 和 DCF 交叉验证。",
      "估值要单独压力测试 AI capex 对未来三年 FCF 的影响。"
    ],
    upgradeConditions: [
      "AI 产品带来可量化 ARPU 或云消耗提升。",
      "Azure 增长保持强于行业且 FCF 转换率稳定。"
    ],
    downgradeConditions: [
      "AI capex 持续上升但收入贡献不清晰。",
      "监管限制捆绑销售或云竞争加剧导致利润率下滑。"
    ],
    risks: [
      "AI 基础设施投入可能压低近期自由现金流转换。",
      "云增长放缓会影响高估值假设。",
      "反垄断和企业软件绑定销售面临监管审查。"
    ],
    openQuestions: [
      "拆分 Azure 增长中 AI 贡献与传统云迁移贡献。",
      "补充 AI capex 对未来三年 FCF margin 的敏感性。"
    ]
  },
  GOOGL: {
    ticker: "GOOGL",
    name: "Alphabet Inc.",
    cik: "0001652044",
    sic: "7370",
    sicDescription: "Services-Computer Programming, Data Processing, Etc.",
    archetype: "Internet Platform",
    facts: {
      revenues: 307000000000,
      grossProfit: 176000000000,
      operatingIncome: 84200000000,
      netIncome: 73800000000,
      freeCashFlow: 69000000000
    },
    metrics: {
      revenueGrowth: "0.0950",
      grossMargin: "0.5733",
      operatingMargin: "0.2743",
      netMargin: "0.2404",
      fcfMargin: "0.2248"
    },
    scenarioGrowth: { bear: 0.03, base: 0.09, bull: 0.14 },
    thesis: "Alphabet 的研究重点是搜索广告韧性、云业务利润率、AI 对搜索体验的影响和监管风险。",
    recommendation: "研究建议：作为 AI 搜索与数字广告重构样本持续跟踪，核心是搜索变现是否被 AI 体验稀释。",
    businessModel: [
      "搜索广告提供现金流，YouTube、Google Cloud 和订阅业务提供增长选项。",
      "AI 既是防御搜索入口的工具，也是可能改变广告点击形态的变量。",
      "云业务需要证明规模利润率，而不是只证明收入增长。"
    ],
    moat: [
      "搜索默认入口、数据反馈循环、广告主网络和 Android/Chrome 分发构成护城河。",
      "反垄断和 AI 搜索替代是主要反证。"
    ],
    industryPosition: [
      "位于数字广告、云和 AI 应用入口交叉处。",
      "同业比较应看广告增长、TAC、云利润率、监管成本和 AI 投入。"
    ],
    valuationRead: [
      "适合 PE、EV/FCF、SOTP 和广告/云分部估值。",
      "估值关键是搜索现金流稳定性与云业务利润率上行空间。"
    ],
    upgradeConditions: [
      "AI 搜索体验没有削弱广告变现，云利润率继续改善。",
      "监管结果未实质破坏分发或广告模式。"
    ],
    downgradeConditions: [
      "搜索广告点击或商业查询变现被 AI 形态稀释。",
      "监管要求改变默认搜索、广告技术栈或数据使用方式。"
    ],
    risks: [
      "AI 搜索形态变化可能影响广告点击和变现效率。",
      "云业务仍需证明规模利润率。",
      "反垄断诉讼和数据隐私监管可能影响商业模式。"
    ],
    openQuestions: [
      "跟踪搜索广告增速、TAC 变化和云业务 operating margin。",
      "评估 Gemini/AI Overview 对搜索 monetization 的长期影响。"
    ]
  },
  AMZN: {
    ticker: "AMZN",
    name: "Amazon.com, Inc.",
    cik: "0001018724",
    sic: "5961",
    sicDescription: "Retail-Catalog & Mail-Order Houses",
    archetype: "Retail / Internet Platform",
    facts: {
      revenues: 575000000000,
      grossProfit: 276000000000,
      operatingIncome: 37000000000,
      netIncome: 30500000000,
      freeCashFlow: 36000000000
    },
    metrics: {
      revenueGrowth: "0.1050",
      grossMargin: "0.4800",
      operatingMargin: "0.0643",
      netMargin: "0.0530",
      fcfMargin: "0.0626"
    },
    scenarioGrowth: { bear: 0.04, base: 0.12, bull: 0.18 },
    thesis: "Amazon 的研究重点是 AWS 增长质量、零售履约效率、广告利润池和 AI 资本开支回报。",
    recommendation: "研究建议：作为云、零售效率和广告利润池复合体持续跟踪，重点验证 AWS 增长与零售利润率修复。",
    businessModel: [
      "零售规模提供流量和履约网络，AWS 与广告贡献利润弹性。",
      "集团质量要分部看：AWS、广告、三方卖家服务和自营零售不能混在一起估值。",
      "现金流质量受库存、履约成本、资本开支和租赁负债影响。"
    ],
    moat: [
      "规模经济、物流网络、Prime 会员、第三方卖家生态和 AWS 客户粘性构成护城河。",
      "反证是履约成本失控、AWS 增速放缓和平台监管。"
    ],
    industryPosition: [
      "位于电商平台、云基础设施和数字广告交叉位置。",
      "同业比较应使用分部利润、资本开支效率和 FCF 转换率。"
    ],
    valuationRead: [
      "适合 SOTP、EV/EBITDA、EV/FCF 和 DCF 交叉验证。",
      "估值关键是 AWS 正常化利润率和零售效率改善能否持续。"
    ],
    upgradeConditions: [
      "AWS 增长恢复且利润率不被 AI capex 明显侵蚀。",
      "零售履约效率继续改善，广告利润池保持增长。"
    ],
    downgradeConditions: [
      "AWS 价格竞争导致利润率下行。",
      "库存、履约和资本开支压低自由现金流质量。"
    ],
    risks: [
      "AWS 增速和价格竞争会影响集团利润弹性。",
      "物流、库存和履约成本可能侵蚀零售利润率。",
      "监管对平台、广告和第三方卖家生态的影响需跟踪。"
    ],
    openQuestions: [
      "拆分 AWS、广告、三方卖家服务的利润贡献。",
      "验证库存周转、履约成本和资本开支回收周期。"
    ]
  },
  KO: {
    ticker: "KO",
    name: "The Coca-Cola Company",
    cik: "0000021344",
    sic: "2086",
    sicDescription: "Bottled and Canned Soft Drinks",
    archetype: "Consumer Goods",
    facts: {
      revenues: 47000000000,
      grossProfit: 28000000000,
      operatingIncome: 12700000000,
      netIncome: 10700000000,
      freeCashFlow: 9600000000
    },
    metrics: {
      revenueGrowth: "0.0600",
      grossMargin: "0.5957",
      operatingMargin: "0.2702",
      netMargin: "0.2277",
      fcfMargin: "0.2043"
    },
    scenarioGrowth: { bear: 0.01, base: 0.04, bull: 0.06 },
    thesis: "Coca-Cola 的研究重点是品牌定价权、渠道库存、销量/价格/组合和新兴市场外汇影响。",
    recommendation: "研究建议：作为消费品定价权和品牌护城河样本跟踪，重点验证销量/价格/组合与渠道库存。",
    businessModel: [
      "品牌授权、浓缩液和装瓶体系形成轻资产现金流结构。",
      "增长质量必须拆成 volume / price / mix，不能只看名义收入。",
      "外汇、装瓶结构和渠道库存会影响可比收入。"
    ],
    moat: [
      "全球品牌、渠道覆盖、营销规模和消费习惯构成护城河。",
      "反证是健康趋势、糖税和价格提升压制销量。"
    ],
    industryPosition: [
      "属于成熟消费品公司，比较重点是定价权、销量韧性和现金回报。",
      "不应使用高成长科技公司的收入倍数框架。"
    ],
    valuationRead: [
      "适合 PE、股息/回购、FCF yield 和 DCF。",
      "估值关键是低增长下现金流稳定性和品牌定价权。"
    ],
    upgradeConditions: [
      "销量稳定且价格/组合贡献不伤害需求。",
      "自由现金流和股东回报保持稳定。"
    ],
    downgradeConditions: [
      "价格提升带来销量下滑或渠道库存恶化。",
      "外汇和监管压力持续侵蚀利润。"
    ],
    risks: [
      "价格提升可能压制销量增长。",
      "糖税、健康消费趋势和包装监管可能影响长期需求。",
      "外汇和装瓶体系结构会影响可比收入与利润质量。"
    ],
    openQuestions: [
      "拆分 volume / price / mix 对增长的贡献。",
      "跟踪渠道库存、装瓶商表现和区域利润率。"
    ]
  },
  JPM: {
    ticker: "JPM",
    name: "JPMorgan Chase & Co.",
    cik: "0000019617",
    sic: "6021",
    sicDescription: "National Commercial Banks",
    archetype: "Bank",
    facts: {
      revenues: 158000000000,
      grossProfit: 158000000000,
      operatingIncome: 59000000000,
      netIncome: 49000000000,
      freeCashFlow: 43000000000
    },
    metrics: {
      revenueGrowth: "0.0800",
      grossMargin: "1.0000",
      operatingMargin: "0.3734",
      netMargin: "0.3101",
      fcfMargin: "0.2722"
    },
    scenarioGrowth: { bear: -0.02, base: 0.03, bull: 0.06 },
    thesis: "JPMorgan 的研究重点是净息收入周期、信贷成本、资本充足率、存款 beta 和投行业务恢复。",
    recommendation: "研究建议：作为银行质量标杆跟踪，但必须使用银行专属指标，不能套用工业企业利润率模型。",
    businessModel: [
      "商业银行、投行、资管和交易业务共同驱动收入。",
      "银行研究核心是资产质量、资本充足、存款成本和利率周期。",
      "自由现金流口径对银行不如资本回报、ROE、CET1 和拨备质量重要。"
    ],
    moat: [
      "规模、品牌、监管牌照、低成本存款和客户关系构成护城河。",
      "反证是信用周期恶化、资本要求提高和存款迁移。"
    ],
    industryPosition: [
      "银行应与大型综合金融机构比较，而非普通周期股或科技股。",
      "重点看 NIM、拨备、不良率、CET1、ROE 和费用效率。"
    ],
    valuationRead: [
      "适合 PB、PE、ROE/COE 和压力测试。",
      "DCF 与工业企业口径不可直接套用。"
    ],
    upgradeConditions: [
      "信用成本可控，CET1 充足且 ROE 高于资本成本。",
      "存款 beta 稳定，净息收入压力可管理。"
    ],
    downgradeConditions: [
      "不良率、拨备和资本要求同步上升。",
      "净息收入下滑且非息收入无法抵消。"
    ],
    risks: [
      "利率下行或存款成本上升可能压缩净息收入。",
      "信用周期恶化会推升拨备和不良贷款。",
      "银行监管资本要求会影响回购和 ROE。"
    ],
    openQuestions: [
      "补充 CET1、NIM、贷款损失准备和存款 beta。",
      "银行不适用部分工业企业指标，需要使用金融机构专属模板。"
    ]
  }
};

export const fallbackAppleResearch = getFallbackCompanyResearch("NVDA");

export function getFallbackCompanyResearch(ticker: string): CompanyResearchResponse {
  const normalizedTicker = normalizeTicker(ticker);
  const profile = fallbackProfiles[normalizedTicker] ?? createAiFallbackProfile(normalizedTicker);
  if (!profile) {
    return unsupportedFallbackResearch(normalizedTicker);
  }

  return createFallbackResearch(profile);
}

function createFallbackResearch(profile: FallbackCompanyProfile): CompanyResearchResponse {
  const aiMetadata = getAiMetadata(profile);
  const sourceUrl = `internal://insightos/fixtures/${profile.ticker.toLowerCase()}-companyfacts`;
  const sourceHash = `synthetic-fixture-${profile.ticker.toLowerCase()}-hash`;
  const scenarios = buildScenarios(profile.facts.freeCashFlow, profile.scenarioGrowth);

  return {
    ticker: profile.ticker,
    status: "completed",
    generated_at: "2026-06-26T00:00:00Z",
    data_source: "SEC EDGAR / SEC XBRL 离线演示数据",
    company: {
      name: profile.name,
      ticker: profile.ticker,
      cik: profile.cik,
      exchange: aiMetadata.exchange,
      industry: aiMetadata.industry,
      description: aiMetadata.description,
      sic: profile.sic,
      sic_description: profile.sicDescription,
      archetype: { name: profile.archetype }
    },
    ai_profile: {
      categories: aiMetadata.categories,
      relevance_score: aiMetadata.relevanceScore,
      reason: aiMetadata.reason
    },
    latest_annual_period: "FY2025",
    filings: [
      {
        accession_number: `${profile.cik}-synthetic-10-k`,
        filing_type: "10-K",
        filed_at: "2025-11-01",
        period_end_date: "2025-09-27",
        primary_document_url: sourceUrl
      }
    ],
    normalized_facts: [
      fact("revenues", profile.facts.revenues, sourceUrl, sourceHash),
      fact("gross_profit", profile.facts.grossProfit, sourceUrl, sourceHash),
      fact("operating_income", profile.facts.operatingIncome, sourceUrl, sourceHash),
      fact("net_income", profile.facts.netIncome, sourceUrl, sourceHash),
      fact("free_cash_flow", profile.facts.freeCashFlow, sourceUrl, sourceHash)
    ],
    financial_quality: [
      metric("revenue_growth", profile.metrics.revenueGrowth, "percent", "(current_revenue - previous_revenue) / previous_revenue"),
      metric("gross_margin", profile.metrics.grossMargin, "ratio", "gross_profit / revenue"),
      metric("operating_margin", profile.metrics.operatingMargin, "ratio", "operating_income / revenue"),
      metric("net_margin", profile.metrics.netMargin, "ratio", "net_income / revenue"),
      metric("free_cash_flow_margin", profile.metrics.fcfMargin, "ratio", "free_cash_flow / revenue"),
      {
        metric: profile.archetype === "Bank" ? "net_interest_margin" : "inventory_turnover",
        status: "unavailable",
        value: null,
        unit: "n/a",
        fiscal_period: "FY2025-FY",
        formula: profile.archetype === "Bank" ? "net_interest_income / average_earning_assets" : "cogs / average_inventory",
        message: "无法可靠计算：需要接入对应经营指标后再计算。"
      }
    ],
    valuation: {
      status: "completed",
      scenarios,
      assumptions: {
        bear_growth: `悲观情景：未来三年自由现金流年复合增长率 ${formatPercent(profile.scenarioGrowth.bear)}`,
        base_growth: `基准情景：未来三年自由现金流年复合增长率 ${formatPercent(profile.scenarioGrowth.base)}`,
        bull_growth: `乐观情景：未来三年自由现金流年复合增长率 ${formatPercent(profile.scenarioGrowth.bull)}`,
        discount_rate: "10%",
        terminal_growth_rate: "2.5%"
      }
    },
    research_report: {
      facts: [
        `${profile.name} 已通过 InsightOS MVP 股票代码映射识别。`,
        `${profile.ticker} 当前使用离线演示财务事实，结构与标准化 SEC XBRL facts 保持一致。`,
        profile.thesis
      ],
      calculations: [
        "gross_margin: gross_profit / revenue",
        "free_cash_flow_margin: free_cash_flow / revenue",
        "bull/base/bear: deterministic three-year FCF growth scenarios"
      ],
      assumptions: [
        "离线演示数据仅在后端连接器不可用时使用。",
        "情景假设为可编辑占位参数，不构成投资建议。"
      ],
      interpretation: [
        "这是用于产品流程验证的第一版研究包。",
        "数据不足的指标会保持“无法可靠计算”，不会用猜测值填充。"
      ],
      risks: profile.risks,
      open_questions: profile.openQuestions
    },
    research_standard: buildResearchStandard(profile),
    investment_committee: {
      conclusion: profile.recommendation,
      action: "行动建议：进入研究跟踪清单；先完成证据链、实时估值和反证检查，再升级为可执行投资备忘录。",
      logic: [
        `好生意：${profile.businessModel[0]}`,
        `护城河：${profile.moat[0]}`,
        `好价格：当前离线模式没有实时股价，因此只能判断估值敏感方向，不能给目标价或实际安全边际。`,
        `反证优先：${profile.downgradeConditions[0]}`
      ],
      conditions_to_upgrade: profile.upgradeConditions,
      conditions_to_downgrade: profile.downgradeConditions,
      compliance_note: "这是研究系统输出的研究建议与跟踪框架，不是针对个人账户、风险偏好或持仓的个性化买卖建议。"
    },
    business_analysis: [
      {
        title: "商业模式与盈利公式",
        summary: profile.thesis,
        bullets: profile.businessModel
      },
      {
        title: "护城河与反证",
        summary: "只把能够持续转化为现金流、利润率或客户留存的优势视为护城河。",
        bullets: profile.moat
      },
      {
        title: "资本配置与现金流质量",
        summary: "用所有者收益和自由现金流质量检验会计利润。",
        bullets: [
          "优先检查自由现金流率、营运资本、库存、应收账款、资本开支和回购/分红质量。",
          "如果利润增长没有同步转化为现金流，企业质量评分应下调。",
          "管理层叙事只能作为待验证材料，不能直接当成事实。"
        ]
      }
    ],
    industry_analysis: [
      {
        title: "产业链位置",
        summary: `${profile.name} 的分析模板归类为 ${profile.archetype}。`,
        bullets: profile.industryPosition
      },
      {
        title: "科技与商业化验证",
        summary: "科技公司不能只判断技术先进性，还要判断商业化路径和利润池归属。",
        bullets: [
          "技术领先要落到客户 ROI、渗透率、替代成本、交付能力和生态锁定。",
          "产业增长要区分结构性需求、周期性补库存和一次性资本开支。",
          "如果增长依赖少数客户或政策窗口，置信度需要打折。"
        ]
      }
    ],
    supply_chain_bottlenecks: buildSupplyChainBottlenecks(profile),
    quality_scorecard: buildScorecard(profile),
    quality_issues: [
      {
        severity: "medium",
        category: "synthetic_fallback",
        message: "当前显示的是合成 fixture。接入后端 SEC 数据后应替换为真实 evidence chain。",
        needs_human_review: false
      }
    ],
    confidence_score: "0.8500",
    sources: [
      {
        source_type: "company_facts",
        source_name: "InsightOS Synthetic SEC Fixture",
        source_url: sourceUrl,
        published_at: "2026-06-26T00:00:00Z",
        retrieved_at: "2026-06-26T00:00:00Z",
        source_hash: sourceHash,
        confidence_score: "0.8500"
      }
    ],
    limitations: [
      "系统不会生成个性化买入/卖出建议。",
      "市场价格数据尚未接入，因此暂不生成交易倍数估值。",
      "当前数字为产品演示 fixture，不是生产市场数据。",
      "投资委员会结论仅代表研究优先级和待验证行动，不代表适合任何个人的交易指令。"
    ]
  };
}

function unsupportedFallbackResearch(ticker: string): CompanyResearchResponse {
  return {
    ticker,
    status: "unsupported",
    generated_at: "2026-06-26T00:00:00Z",
    data_source: "暂无可验证公司数据",
    company: {
      name: `${ticker} 研究包暂不可用`,
      ticker,
      cik: "unknown",
      exchange: "unknown",
      industry: "unknown",
      description: "暂无可追溯公司信息。",
      archetype: { name: "Unmapped" }
    },
    ai_profile: {
      categories: [],
      relevance_score: 0,
      reason: "缺少可验证公司数据，无法判断 AI 产业链相关性。"
    },
    latest_annual_period: "unknown",
    filings: [],
    normalized_facts: [],
    financial_quality: [
      {
        metric: "research_packet",
        status: "unavailable",
        value: null,
        unit: "n/a",
        fiscal_period: "unknown",
        formula: "requires_supported_ticker_or_live_connector",
        message: `当前离线演示支持 ${supportedFallbackTickers.join(", ")}。${ticker} 需要后端 SEC connector 返回可验证数据。`
      }
    ],
    valuation: {
      status: "unavailable",
      scenarios: {},
      assumptions: {}
    },
    research_report: {
      facts: [`${ticker} 不在当前离线 MVP 演示股票池中。`],
      calculations: ["无法可靠计算：缺少可验证财务事实。"],
      assumptions: ["不使用无法追溯来源的字段。"],
      interpretation: ["请接入后端 SEC 数据或选择 MVP 支持 ticker。"],
      risks: ["缺少公司证据链时不应生成财务结论。"],
      open_questions: [`选择 ${supportedFallbackTickers.join(", ")}，或启动后端 SEC connector 后重试 ${ticker}。`]
    },
    research_standard: buildResearchStandard(),
    investment_committee: {
      conclusion: "研究结论：证据不足，不能形成公司质量、估值或投资吸引力判断。",
      action: "行动建议：先补齐可验证数据，不进入投资委员会讨论。",
      logic: ["没有 filings、财务事实、价格和证据链时，系统必须停止生成结论。"],
      conditions_to_upgrade: ["后端 SEC connector 返回可验证 company facts、filings 和标准化财务事实。"],
      conditions_to_downgrade: ["仍然无法获取可追溯数据，或关键来源冲突无法解释。"],
      compliance_note: "这是研究流程状态，不是个性化投资建议。"
    },
    business_analysis: [],
    industry_analysis: [],
    supply_chain_bottlenecks: [],
    quality_scorecard: [],
    quality_issues: [
      {
        severity: "high",
        category: "missing_evidence",
        message: "离线模式下没有该股票的可追溯证据链。",
        needs_human_review: true
      }
    ],
    confidence_score: "0.2000",
    sources: [],
    limitations: [
      "系统不会生成个性化买入/卖出建议。",
      "没有可追溯财务事实时，不生成计算结果。"
    ]
  };
}

function metric(
  name: string,
  value: string,
  unit: string,
  formula: string
): CalculationResult {
  return {
    metric: name,
    status: "ok",
    value,
    unit,
    fiscal_period: "FY2025-FY",
    formula
  };
}

function fact(
  metricName: string,
  value: number,
  sourceUrl: string,
  sourceHash: string
): NormalizedFact {
  return {
    metric_name: metricName,
    value,
    unit: "USD",
    fiscal_period: "FY2025-FY",
    fiscal_year: 2025,
    filed_at: "2025-11-01",
    source_url: sourceUrl,
    source_hash: sourceHash
  };
}

function buildScenarios(
  baseFreeCashFlow: number,
  growthRates: FallbackCompanyProfile["scenarioGrowth"]
): Record<string, number[]> {
  return {
    bear: projectCashFlows(baseFreeCashFlow, growthRates.bear),
    base: projectCashFlows(baseFreeCashFlow, growthRates.base),
    bull: projectCashFlows(baseFreeCashFlow, growthRates.bull)
  };
}

function projectCashFlows(baseFreeCashFlow: number, growthRate: number): number[] {
  return [1, 2, 3].map((year) => Math.round(baseFreeCashFlow * (1 + growthRate) ** year));
}

function createAiFallbackProfile(ticker: string): FallbackCompanyProfile | null {
  const metadata = aiCompanyMetadata[ticker];
  if (!metadata) {
    return null;
  }

  const seed = Math.max(1, metadata.relevanceScore);
  const revenue = Math.round((20_000_000_000 + seed * 800_000_000) / 1_000_000_000) * 1_000_000_000;
  const grossMargin = metadata.archetype.includes("Software") ? 0.72 : 0.56;
  const operatingMargin = metadata.archetype.includes("Equipment") ? 0.28 : metadata.archetype.includes("Semiconductor") ? 0.31 : 0.24;
  const netMargin = operatingMargin * 0.78;
  const fcfMargin = operatingMargin * 0.72;

  return {
    ticker,
    name: metadata.name,
    cik: metadata.cik,
    exchange: metadata.exchange,
    industry: metadata.industry,
    description: metadata.description,
    aiCategories: metadata.categories,
    aiRelevanceScore: metadata.relevanceScore,
    aiReason: metadata.reason,
    sic: metadata.sic,
    sicDescription: metadata.sicDescription,
    archetype: metadata.archetype,
    facts: {
      revenues: revenue,
      grossProfit: Math.round(revenue * grossMargin),
      operatingIncome: Math.round(revenue * operatingMargin),
      netIncome: Math.round(revenue * netMargin),
      freeCashFlow: Math.round(revenue * fcfMargin)
    },
    metrics: {
      revenueGrowth: (metadata.relevanceScore / 1000 + 0.03).toFixed(4),
      grossMargin: grossMargin.toFixed(4),
      operatingMargin: operatingMargin.toFixed(4),
      netMargin: netMargin.toFixed(4),
      fcfMargin: fcfMargin.toFixed(4)
    },
    scenarioGrowth: {
      bear: 0.02,
      base: metadata.relevanceScore >= 85 ? 0.12 : 0.08,
      bull: metadata.relevanceScore >= 85 ? 0.2 : 0.14
    },
    thesis: `${metadata.name} 的研究重点是 ${metadata.categories.join("、")} 中的商业化质量、竞争位置和现金流转换。`,
    recommendation: `研究建议：纳入 AI 产业链观察池，优先验证 ${metadata.reason}`,
    businessModel: [
      metadata.description,
      "第一阶段使用合成演示财务数据验证研究流程，后续必须由 SEC filings 和 company facts 替换。",
      "核心问题是 AI 相关收入能否转化为可持续利润率、自由现金流和客户留存。"
    ],
    moat: [
      "需要用客户留存、产品差异化、生态锁定、规模经济和资本效率验证竞争优势。",
      "若 AI 相关收入依赖少数客户、一次性项目或周期性资本开支，护城河评分应下调。",
      "管理层叙事必须与财务事实和外部证据交叉验证。"
    ],
    industryPosition: [
      `AI 产业链分类：${metadata.categories.join(" / ")}。`,
      metadata.reason,
      "同业比较应优先选择同一产业链位置，而不是简单按市值或行业代码比较。"
    ],
    valuationRead: [
      "当前缺少实时价格，不能生成真实 PE/PS/EV/FCF 判断。",
      "估值应在接入价格后同时检查增长、利润率、FCF 转换率和同业倍数。",
      "若 AI 相关性高但现金流证据弱，应提高估值折现和风险权重。"
    ],
    upgradeConditions: [
      "SEC 数据和公司披露能证明 AI 相关收入正在扩大且质量高。",
      "毛利率、自由现金流率或客户留存能够支撑当前增长叙事。"
    ],
    downgradeConditions: [
      "AI 相关订单或收入无法在 filings、IR 或财务数据中得到验证。",
      "收入增长依赖一次性资本开支、客户集中或估值假设过度乐观。"
    ],
    risks: [
      "合成演示数据不能替代真实财务数据。",
      "AI 需求、客户集中度、竞争加剧和资本开支周期可能改变增长路径。",
      "估值对增长和利润率假设敏感。"
    ],
    openQuestions: [
      "接入最新 10-K/10-Q 后验证 AI 相关收入披露。",
      "补充同业比较、价格数据和真实估值倍数。"
    ]
  };
}

function getAiMetadata(profile: FallbackCompanyProfile): AiCompanyMetadata {
  return (
    aiCompanyMetadata[profile.ticker] ?? {
      name: profile.name,
      cik: profile.cik,
      exchange: profile.exchange ?? "NASDAQ",
      industry: profile.industry ?? profile.archetype,
      description: profile.description ?? profile.thesis,
      categories: profile.aiCategories ?? ["其他"],
      relevanceScore: profile.aiRelevanceScore ?? 50,
      reason: profile.aiReason ?? "该公司不在 BRD 第一阶段 AI 股票池中，仅保留为历史演示模板。",
      archetype: profile.archetype,
      sic: profile.sic,
      sicDescription: profile.sicDescription
    }
  );
}

function buildResearchStandard(profile?: FallbackCompanyProfile): ResearchStandardSection[] {
  return [
    {
      title: "好生意",
      principle: "先判断公司能否长期产生高质量现金流，而不是先看短期股价。",
      checklist: [
        "商业模式是否简单可解释，收入从哪里来，客户为什么持续付费。",
        "增长是否由真实需求、复购和渗透率驱动，而不是一次性补库存。",
        profile ? `当前公司模板：${profile.archetype}，必须使用行业适配指标。` : "必须先完成行业模板匹配。"
      ]
    },
    {
      title: "护城河",
      principle: "护城河必须能体现在定价权、客户留存、成本优势、网络效应或资本效率上。",
      checklist: [
        "优势是否可持续，是否被竞争、监管、替代技术或客户自研削弱。",
        "管理层表述只能作为待验证观点，不能替代数据证据。",
        "必须列出至少三个可能推翻多头逻辑的反证。"
      ]
    },
    {
      title: "好价格",
      principle: "估值不是预测一个精确价格，而是检验增长、利润率和现金流假设是否有安全边际。",
      checklist: [
        "DCF、PE、EV/Sales 或行业适配估值必须交叉验证。",
        "必须展示 Bull/Base/Bear 情景和使结论失效的敏感变量。",
        "没有实时股价时，只能输出研究判断，不能输出目标价或交易建议。"
      ]
    }
  ];
}

function buildScorecard(profile: FallbackCompanyProfile): ScorecardItem[] {
  const growth = Number(profile.metrics.revenueGrowth);
  const margin = Number(profile.metrics.operatingMargin);
  const fcf = Number(profile.metrics.fcfMargin);
  return [
    {
      label: "企业质量",
      score: clampScore(Math.round(62 + margin * 45 + fcf * 22)),
      rationale: "基于营业利润率、自由现金流率、商业模式韧性和护城河描述的演示评分。"
    },
    {
      label: "行业景气度",
      score: clampScore(Math.round(58 + growth * 90)),
      rationale: "基于收入增长、产业链位置和未来三年需求假设的演示评分。"
    },
    {
      label: "估值清晰度",
      score: 54,
      rationale: "缺少实时价格与市场倍数，估值结论只能做敏感性方向判断。"
    },
    {
      label: "研究完整度",
      score: 76,
      rationale: "已包含商业模式、产业链、财务质量、估值情景、反证和行动条件；仍需真实数据源替换 fixture。"
    }
  ];
}

function buildSupplyChainBottlenecks(profile: FallbackCompanyProfile): SupplyChainBottleneck[] {
  if (profile.ticker === "NVDA") {
    return [
      {
        stage: "上游：HBM 高带宽内存",
        bottleneck: "HBM3E/HBM4 供给、良率和与 GPU 封装协同认证可能限制 AI 加速器出货节奏。",
        expected_window: "2026H1-2027H1 最需要跟踪；若 HBM4 转换顺利，压力可能在 2027H2 起缓和。",
        estimated_duration: "约 4-6 个季度，取决于 SK Hynix、Micron、Samsung 的有效产能和客户认证进度。",
        severity: "critical",
        involved_companies: ["SK Hynix", "Micron", "Samsung Electronics", "NVIDIA", "TSMC"],
        likely_beneficiaries: ["SK Hynix", "Micron", "Samsung Electronics", "HBM 设备与材料供应商"],
        investment_implication:
          "如果 HBM 继续紧缺，Nvidia 收入确认可能受供给约束，但 HBM 供应商议价和利润弹性更直接；若 HBM 过快扩产，则需警惕 2027 后价格正常化。",
        watch_metrics: [
          "HBM 产能扩张计划与客户认证节点",
          "Nvidia 数据中心收入增速和递延/未履约订单线索",
          "HBM 合约价格、良率、库存周转和毛利率"
        ],
        evidence_date: "2026-06-28",
        confidence_score: 0.78
      },
      {
        stage: "中游：先进封装 CoWoS / CoWoS-L",
        bottleneck: "GPU、HBM 与基板的先进封装产能可能是 Blackwell/Rubin 世代放量的关键约束。",
        expected_window: "2025H2-2026H2 为高风险窗口；新增产能释放后，约在 2027 年边际缓和。",
        estimated_duration: "约 5-8 个季度，取决于 TSMC CoWoS 扩产、基板供应和封装良率爬坡。",
        severity: "critical",
        involved_companies: ["TSMC", "NVIDIA", "ASE Technology", "Amkor", "Ibiden", "Unimicron"],
        likely_beneficiaries: ["TSMC", "ASE Technology", "Amkor", "高端 ABF/载板供应商"],
        investment_implication:
          "若 CoWoS 仍是瓶颈，Nvidia 的高端 GPU 交付节奏会受限，先进封装和载板链条更可能捕获瓶颈租金。",
        watch_metrics: [
          "TSMC 先进封装产能扩张指引",
          "CoWoS 交期、单位封装价格和良率",
          "Nvidia 新平台交付周期与客户排队时间"
        ],
        evidence_date: "2026-06-28",
        confidence_score: 0.8
      },
      {
        stage: "上游：先进制程晶圆与 EUV 产能",
        bottleneck: "前沿节点晶圆供给通常不如 HBM/封装短期尖锐，但在新平台切换期会影响成本、良率和交付。",
        expected_window: "2026-2028，随 Rubin 及后续平台、N3/N2 节点迁移而变化。",
        estimated_duration: "多年度结构性约束，但单季波动低于 HBM 和先进封装。",
        severity: "medium",
        involved_companies: ["TSMC", "ASML", "Applied Materials", "Lam Research", "Tokyo Electron", "NVIDIA"],
        likely_beneficiaries: ["TSMC", "ASML", "前沿制程设备供应商"],
        investment_implication:
          "这是长期资本开支和制程领先者受益链，不一定直接决定下季度 Nvidia 收入，但会影响长期毛利率和平台节奏。",
        watch_metrics: [
          "TSMC 前沿节点 capex 与利用率",
          "EUV 设备交付和装机周期",
          "Nvidia 新平台良率和单位成本变化"
        ],
        evidence_date: "2026-06-28",
        confidence_score: 0.66
      },
      {
        stage: "下游：AI 服务器、电力与散热",
        bottleneck: "从芯片到可部署算力还需要整机、机柜、液冷、电源和数据中心电力容量，可能把芯片需求延后为交付周期问题。",
        expected_window: "2026-2028，尤其是高功耗 AI rack 从风冷向液冷迁移阶段。",
        estimated_duration: "约 6-10 个季度；区域电力接入可能更久。",
        severity: "high",
        involved_companies: [
          "Foxconn",
          "Quanta",
          "Wistron",
          "Supermicro",
          "Dell Technologies",
          "Vertiv",
          "Eaton",
          "Schneider Electric"
        ],
        likely_beneficiaries: ["Vertiv", "Eaton", "Schneider Electric", "AI server ODM/OEM", "液冷与电源管理供应商"],
        investment_implication:
          "如果数据中心电力/散热成为主约束，Nvidia 芯片需求不会消失，但收入节奏可能后移；电力、液冷和整机链条可能获得更直接订单弹性。",
        watch_metrics: [
          "云厂商数据中心 capex 与电力接入周期",
          "AI 服务器交期、液冷渗透率、rack 功耗",
          "电源、UPS、热管理公司订单和 backlog"
        ],
        evidence_date: "2026-06-28",
        confidence_score: 0.72
      },
      {
        stage: "需求端：云厂商资本开支消化",
        bottleneck: "真实瓶颈可能从供给转向客户 ROI：云厂商需要把 GPU 集群转化为可收费推理、训练或企业 AI 服务。",
        expected_window: "2026H2-2027H2，是判断 AI 芯片需求可持续性的核心窗口。",
        estimated_duration: "约 4-8 个季度；若推理收入增长不足，消化期可能拉长。",
        severity: "high",
        involved_companies: ["Microsoft", "Amazon", "Alphabet", "Meta", "Oracle", "NVIDIA"],
        likely_beneficiaries: ["能证明 AI 云收入回收期的云平台", "推理软件与模型服务生态", "高利用率 GPU 云服务商"],
        investment_implication:
          "如果客户 capex ROI 被证实，Nvidia 高增长假设更稳；若 GPU 利用率或 AI 收入低于预期，估值应先降级而不是等收入下滑。",
        watch_metrics: [
          "云厂商 AI capex、折旧压力和 AI 收入披露",
          "GPU 利用率、租赁价格、推理 token 成本",
          "Nvidia 客户集中度和订单取消/延后线索"
        ],
        evidence_date: "2026-06-28",
        confidence_score: 0.7
      }
    ];
  }

  return [
    {
      stage: "行业适配瓶颈",
      bottleneck: `${profile.archetype} 模板当前仅完成轻量瓶颈映射，需要接入行业数据后细化。`,
      expected_window: "待行业数据接入后判断",
      estimated_duration: "无法可靠估计",
      severity: "medium",
      involved_companies: [profile.name],
      likely_beneficiaries: ["需要行业数据后确认"],
      investment_implication: "当前不把瓶颈分析作为估值升级依据。",
      watch_metrics: profile.archetype === "Consumer Goods"
        ? ["volume / price / mix", "渠道库存", "原材料成本", "客户集中度"]
        : ["订单 backlog", "产能利用率", "供应商交期", "客户集中度"],
      evidence_date: "2026-06-28",
      confidence_score: 0.35
    }
  ];
}

function clampScore(score: number): number {
  return Math.max(0, Math.min(100, score));
}

function normalizeTicker(ticker: string): string {
  const normalized = ticker.trim().toUpperCase();
  return companyNameAliases[normalized] ?? (normalized || "NVDA");
}

function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}
