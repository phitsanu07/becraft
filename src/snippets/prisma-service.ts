/**
 * Snippet: PrismaService for NestJS
 *
 * Used by: bootstrap-agent (when stack = Prisma)
 * Customize: usually no changes needed
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(PrismaService.name);

  async onModuleInit() {
    await this.$connect();
    this.logger.log('Prisma connected');
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('Prisma disconnected');
  }
}

// Companion module file (prisma.module.ts):
//
// import { Global, Module } from '@nestjs/common';
// import { PrismaService } from './prisma.service';
//
// @Global()
// @Module({
//   providers: [PrismaService],
//   exports: [PrismaService],
// })
// export class PrismaModule {}
