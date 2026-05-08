/**
 * Snippet: Swagger / OpenAPI setup for NestJS
 *
 * Used by: bootstrap-agent (called from main.ts)
 * Customize: title, description, tags
 */

import { INestApplication } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

export interface SwaggerOptions {
  title: string;
  description?: string;
  version?: string;
  path?: string;
  tags?: string[];
}

export function setupSwagger(app: INestApplication, options: SwaggerOptions) {
  const builder = new DocumentBuilder()
    .setTitle(options.title)
    .setDescription(options.description || `${options.title} API`)
    .setVersion(options.version || '1.0')
    .addBearerAuth();

  for (const tag of options.tags || []) {
    builder.addTag(tag);
  }

  const config = builder.build();
  const document = SwaggerModule.createDocument(app, config);

  SwaggerModule.setup(options.path || 'docs', app, document, {
    swaggerOptions: {
      persistAuthorization: true,
      tagsSorter: 'alpha',
      operationsSorter: 'alpha',
    },
  });
}

// Usage in main.ts:
//
// import { setupSwagger } from './common/swagger';
//
// setupSwagger(app, {
//   title: 'My API',
//   description: 'My backend API',
//   tags: ['users', 'products'],
// });
