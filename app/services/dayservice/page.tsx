import ServiceHandbook from "../../../components/service-handbook";
import { serviceHandbook } from "../../../lib/working-handbook";
import { pageMetadata } from "../../../lib/site-metadata";

export const metadata = pageMetadata("通所介護の手引", "開設・人員・設備・運営・報酬など15章の手引と、関連する法令・通知・Q&A。", "/services/dayservice", false);

export default function ServicePage() {
  return <ServiceHandbook service={serviceHandbook("dayservice")!} />;
}
