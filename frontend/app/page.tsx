import { DemoResearchPanel } from "@/src/components/DemoResearchPanel";
import { HealthPanel } from "@/src/components/HealthPanel";
import { SingleStockResearchPanel } from "@/src/components/SingleStockResearchPanel";

export default function Home() {
  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">InsightOS MVP</p>
          <h1>可验证的 AI 投资研究工作台</h1>
          <p className="lede">
            当前骨架已包含 Next.js 前端、FastAPI 后端、PostgreSQL、Redis 和 Docker Compose。
          </p>
        </div>
        <HealthPanel />
      </section>
      <SingleStockResearchPanel />
      <DemoResearchPanel />
    </main>
  );
}
