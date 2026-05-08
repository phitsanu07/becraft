/**
 * Snippet: NestJS bootstrap (main.ts skeleton)
 *
 * Customize:
 *   - Replace {{APP_NAME}} with actual app name
 *   - Adjust trust proxy if behind proxy/load balancer
 *   - Adjust port via PORT env var
 *
 * Used by: bootstrap-agent
 */

import { NestFactory } from '@nestjs/core';
import { ValidationPipe, VersioningType } from '@nestjs/common';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { Logger } from 'nestjs-pino';
import * as cookieParser from 'cookie-parser';
import helmet from 'helmet';

import { AppModule } from './app.module';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bufferLogs: true });

  // Use Pino as global logger
  app.useLogger(app.get(Logger));

  // Security headers
  app.use(helmet());

  // Cookies
  app.use(cookieParser());

  // CORS
  app.enableCors({
    origin: process.env.CORS_ORIGIN?.split(',') || true,
    credentials: true,
  });

  // Trust proxy for X-Forwarded-* headers (set to 1 for single proxy)
  app.set?.('trust proxy', 1);

  // API versioning: /api/v1/...
  app.setGlobalPrefix('api');
  app.enableVersioning({
    type: VersioningType.URI,
    prefix: 'v',
    defaultVersion: '1',
  });

  // Global validation
  app.useGlobalPipes(
    new ValidationPipe({
      transform: true,
      whitelist: true,
      forbidNonWhitelisted: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // Global exception filter (RFC 7807)
  app.useGlobalFilters(new AllExceptionsFilter());

  // Graceful shutdown
  app.enableShutdownHooks();

  // Swagger / OpenAPI
  const swaggerConfig = new DocumentBuilder()
    .setTitle(process.env.APP_NAME || '{{APP_NAME}}')
    .setDescription('{{APP_NAME}} backend API')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('docs', app, document, {
    swaggerOptions: { persistAuthorization: true },
  });

  const port = parseInt(process.env.PORT || '3000', 10);
  await app.listen(port);

  const logger = app.get(Logger);
  logger.log(`🚀 API listening on http://localhost:${port}`);
  logger.log(`📖 OpenAPI docs at http://localhost:${port}/docs`);
  logger.log(`🏥 Health check at http://localhost:${port}/health`);
}

bootstrap();
