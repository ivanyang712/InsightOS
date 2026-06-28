export type AiCompanyMetadata = {
  name: string;
  cik: string;
  exchange: string;
  industry: string;
  description: string;
  categories: string[];
  relevanceScore: number;
  reason: string;
  archetype: string;
  sic: string;
  sicDescription: string;
};

export const supportedFallbackTickers = [
  "NVDA",
  "MSFT",
  "GOOGL",
  "AMZN",
  "META",
  "AMD",
  "AVGO",
  "TSM",
  "ASML",
  "PLTR"
];

export const companyNameAliases: Record<string, string> = {
  NVIDIA: "NVDA",
  MICROSOFT: "MSFT",
  GOOGLE: "GOOGL",
  ALPHABET: "GOOGL",
  AMAZON: "AMZN",
  META: "META",
  FACEBOOK: "META",
  AMD: "AMD",
  BROADCOM: "AVGO",
  TSMC: "TSM",
  ASML: "ASML",
  PALANTIR: "PLTR"
};

export const aiCompanyMetadata: Record<string, AiCompanyMetadata> = {
  NVDA: {
    name: "NVIDIA Corporation",
    cik: "0001045810",
    exchange: "NASDAQ",
    industry: "Semiconductors",
    description: "AI 加速器、GPU、网络和加速计算平台供应商。",
    categories: ["AI 芯片", "数据中心", "AI 软件生态"],
    relevanceScore: 95,
    reason: "数据中心 GPU、加速计算平台和 CUDA 生态处于 AI 基础设施核心环节。",
    archetype: "Semiconductor",
    sic: "3674",
    sicDescription: "Semiconductors and Related Devices"
  },
  MSFT: {
    name: "Microsoft Corporation",
    cik: "0000789019",
    exchange: "NASDAQ",
    industry: "Software / Cloud",
    description: "企业软件、Azure 云、AI 应用和开发者生态平台。",
    categories: ["云计算", "企业 AI 应用", "AI 软件"],
    relevanceScore: 90,
    reason: "Azure、Copilot、OpenAI 生态和企业软件分发构成 AI 应用与基础设施入口。",
    archetype: "SaaS / Software",
    sic: "7372",
    sicDescription: "Services-Prepackaged Software"
  },
  GOOGL: {
    name: "Alphabet Inc.",
    cik: "0001652044",
    exchange: "NASDAQ",
    industry: "Internet Platform / Cloud",
    description: "搜索广告、YouTube、Google Cloud 和 Gemini AI 平台。",
    categories: ["云计算", "AI 软件", "AI 应用平台"],
    relevanceScore: 88,
    reason: "搜索、云、Gemini 和 TPU 生态使其同时处于 AI 应用与基础设施层。",
    archetype: "Internet Platform",
    sic: "7370",
    sicDescription: "Services-Computer Programming, Data Processing, Etc."
  },
  AMZN: {
    name: "Amazon.com, Inc.",
    cik: "0001018724",
    exchange: "NASDAQ",
    industry: "Cloud / Retail Platform",
    description: "AWS 云、AI 基础设施、广告和电商平台。",
    categories: ["云计算", "数据中心", "AI 基础设施"],
    relevanceScore: 86,
    reason: "AWS 是 AI 训练、推理和企业云部署的重要基础设施平台。",
    archetype: "Retail / Internet Platform",
    sic: "5961",
    sicDescription: "Retail-Catalog & Mail-Order Houses"
  },
  META: {
    name: "Meta Platforms, Inc.",
    cik: "0001326801",
    exchange: "NASDAQ",
    industry: "Internet Platform",
    description: "社交平台、广告系统、开源大模型和 AI 推荐基础设施。",
    categories: ["AI 应用平台", "AI 软件", "数据中心"],
    relevanceScore: 84,
    reason: "AI 推荐、广告投放、大模型和自建数据中心资本开支对 AI 产业链影响大。",
    archetype: "Internet Platform",
    sic: "7370",
    sicDescription: "Services-Computer Programming, Data Processing, Etc."
  },
  AMD: {
    name: "Advanced Micro Devices, Inc.",
    cik: "0000002488",
    exchange: "NASDAQ",
    industry: "Semiconductors",
    description: "CPU、GPU、数据中心加速器和嵌入式芯片公司。",
    categories: ["AI 芯片", "数据中心", "半导体制造生态"],
    relevanceScore: 82,
    reason: "MI 系列加速器和 EPYC 数据中心平台是 Nvidia 之外的重要 AI 算力供给。",
    archetype: "Semiconductor",
    sic: "3674",
    sicDescription: "Semiconductors and Related Devices"
  },
  AVGO: {
    name: "Broadcom Inc.",
    cik: "0001730168",
    exchange: "NASDAQ",
    industry: "Semiconductors / Infrastructure Software",
    description: "网络芯片、定制 ASIC、互连和基础设施软件供应商。",
    categories: ["AI 芯片", "数据中心", "网络基础设施"],
    relevanceScore: 83,
    reason: "定制 AI ASIC、交换芯片和高速互连受益于云厂商 AI 集群建设。",
    archetype: "Semiconductor",
    sic: "3674",
    sicDescription: "Semiconductors and Related Devices"
  },
  TSM: {
    name: "Taiwan Semiconductor Manufacturing Company Limited",
    cik: "0001046179",
    exchange: "NYSE",
    industry: "Semiconductor Foundry",
    description: "全球领先晶圆代工厂，服务前沿制程和先进封装需求。",
    categories: ["半导体制造", "AI 芯片供应链", "先进封装"],
    relevanceScore: 92,
    reason: "AI 芯片前沿制程和先进封装产能高度依赖 TSMC。",
    archetype: "Semiconductor",
    sic: "3674",
    sicDescription: "Semiconductors and Related Devices"
  },
  ASML: {
    name: "ASML Holding N.V.",
    cik: "0000937966",
    exchange: "NASDAQ",
    industry: "Semiconductor Equipment",
    description: "EUV/DUV 光刻设备供应商，是先进制程扩产核心设备公司。",
    categories: ["半导体设备", "半导体制造", "AI 芯片供应链"],
    relevanceScore: 89,
    reason: "AI 芯片制造的先进节点扩产依赖 EUV 光刻设备能力。",
    archetype: "Semiconductor Equipment",
    sic: "3559",
    sicDescription: "Special Industry Machinery"
  },
  PLTR: {
    name: "Palantir Technologies Inc.",
    cik: "0001321655",
    exchange: "NYSE",
    industry: "AI Software",
    description: "数据操作系统、企业 AI 平台和政府/商业数据分析软件公司。",
    categories: ["AI 软件", "企业 AI 应用", "数据基础设施"],
    relevanceScore: 78,
    reason: "AIP 和数据平台定位企业 AI 落地层，关键在商业化速度和单位经济性。",
    archetype: "SaaS / Software",
    sic: "7372",
    sicDescription: "Services-Prepackaged Software"
  }
};
