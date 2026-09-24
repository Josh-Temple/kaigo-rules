import { NextResponse } from "next/server";
import contextData from "../../../../../../../data/context-packages/dayservice-questions.generated.json";

type Params = Promise<{ serviceId: string; slug: string }>;

const data = contextData as any;

export async function GET(
  _request: Request,
  { params }: { params: Params }
) {
  const { serviceId, slug } = await params;

  if (serviceId !== data.service_id) {
    return NextResponse.json(
      { error: "SERVICE_CONTEXT_NOT_AVAILABLE", service_id: serviceId },
      { status: 404 }
    );
  }

  const packageData = (data.packages || []).find(
    (item: any) => item.question?.slug === slug
  );

  if (!packageData) {
    return NextResponse.json(
      { error: "QUESTION_CONTEXT_NOT_FOUND", service_id: serviceId, slug },
      { status: 404 }
    );
  }

  return NextResponse.json({
    format_version: data.format_version,
    package_kind: data.package_kind,
    policy: data.policy,
    package: packageData,
  });
}
