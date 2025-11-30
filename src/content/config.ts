import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
	type: 'content',
	schema: z.object({
		title: z.string(),
		description: z.string(),
		pubDate: z.coerce.date(),
		updatedDate: z.coerce.date().optional(),
		heroImage: z.string().optional(),
		tags: z.array(z.string()).optional(),
		category: z.enum(['indie-dev', 'ai-ml', 'it-tech']).optional(),
		affiliateLinks: z.array(z.object({
			text: z.string(),
			url: z.string(),
		})).optional(),
	}),
});

export const collections = { posts };
