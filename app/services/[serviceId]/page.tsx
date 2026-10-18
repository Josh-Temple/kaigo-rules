import { notFound } from "next/navigation";
import ServiceHandbook from "../../../components/service-handbook";
import { serviceHandbook, serviceHandbooks } from "../../../lib/working-handbook";
import { pageMetadata } from "../../../lib/site-metadata";

export const dynamicParams = false;
export function generateStaticParams() {
  return serviceHandbooks.filter(s => !["dayservice", "dayrehab"].includes(s.service_id)).map(s => ({ serviceId: s.service_id }));
}
export async function generateMetadata({ params }: { params: Promise<{ serviceId: string }> }) {
  const { serviceId } = await params;
  const service = serviceHandbook(serviceId);
  if (!service) notFound();
  return pageMetadata(service.label + "の手引", "開設・人員・設備・運営・報酬など15章の手引と関連する法令・通知・Q&A。", `/services/${serviceId}`);
}
export default async function ServicePage({ params }: { params: Promise<{ serviceId: string }> }) {
  const service = serviceHandbook((await params).serviceId);
  if (!service) notFound();
  return <ServiceHandbook service={service} />;
}
