import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: z.looseObject({
    title: z.string(),
    principles: z.array(z.object({
      title: z.string(),
      description: z.string(),
    })).optional(),
    cta: z.object({
      heading: z.string(),
      description: z.string(),
      primary: z.object({
        text: z.string(),
        url: z.string(),
      }),
      secondary: z.object({
        text: z.string(),
        url: z.string(),
      }),
    }).optional(),
    email_label: z.string().optional(),
    email: z.string().optional(),
    card_detail: z.string().optional(),
  }),
});

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    authors: z.array(z.string()),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().optional().default(false),
  }),
});

export const collections = { pages, blog };
