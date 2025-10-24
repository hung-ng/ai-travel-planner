import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from '../src/app/page';

describe('Home Page', () => {
    beforeEach(() => {
        render(<Home />);
    });

    describe('Page Structure', () => {
        it('renders the main container with correct styling', () => {
            const main = screen.getByRole('main');
            expect(main).toBeInTheDocument();
            expect(main).toHaveClass('min-h-screen', 'p-8');
        });

        it('renders the maximum width container', () => {
            const container = screen.getByRole('main').querySelector('.max-w-6xl');
            expect(container).toBeInTheDocument();
            expect(container).toHaveClass('mx-auto');
        });
    });

    describe('Header Section', () => {
        it('renders the main heading with correct text and styling', () => {
            const heading = screen.getByRole('heading', { level: 1 });
            expect(heading).toBeInTheDocument();
            expect(heading).toHaveTextContent('Welcome to AI Travel Planner');
            expect(heading).toHaveClass(
                'text-5xl',
                'font-bold',
                'mb-4',
                'bg-gradient-to-r',
                'from-blue-600',
                'to-purple-600',
                'bg-clip-text',
                'text-transparent'
            );
        });

        it('renders the subtitle with correct text', () => {
            const subtitle = screen.getByText(
                'Plan your trips with AI-powered tools. Discover new places, create itineraries, and get personalized recommendations.'
            );
            expect(subtitle).toBeInTheDocument();
            expect(subtitle).toHaveClass('text-xl', 'text-gray-600');
        });
    });

    describe('Main Content Section', () => {
        it('renders the "Get Started On Your Journey" heading', () => {
            const heading = screen.getByRole('heading', { level: 2 });
            expect(heading).toBeInTheDocument();
            expect(heading).toHaveTextContent('Get Started On Your Journey');
            expect(heading).toHaveClass('text-3xl', 'font-bold', 'mb-4');
        });

        it('renders the description paragraph', () => {
            const description = screen.getByText(
                'Chat with our AI assistant to create personalized itineraries, discover hidden gems, and plan every detail of your perfect trip.'
            );
            expect(description).toBeInTheDocument();
            expect(description).toHaveClass('text-gray-600', 'mb-6');
        });

        it('renders all feature list items', () => {
            const features = [
                'AI-powered recommendations',
                'Personalized itineraries',
                'Budget-conscious planning',
                'Tailored to your interests'
            ];

            features.forEach(feature => {
                expect(screen.getByText(feature)).toBeInTheDocument();
            });
        });

        it('renders feature list items with correct styling', () => {
            const featureItems = screen.getAllByText(/AI-powered recommendations|Personalized itineraries|Budget-conscious planning|Tailored to your interests/);

            featureItems.forEach(item => {
                const listItem = item.closest('li');
                expect(listItem).toHaveClass('flex', 'items-center', 'text-gray-700');
            });
        });
    });

    describe('Call-to-Action Section', () => {
        it('renders the "Start Planning Now" button as a link', () => {
            const ctaButton = screen.getByRole('link', { name: 'Start Planning Now' });
            expect(ctaButton).toBeInTheDocument();
            expect(ctaButton).toHaveAttribute('href', '/chat');
        });

        it('applies correct styling to the CTA button', () => {
            const ctaButton = screen.getByRole('link', { name: 'Start Planning Now' });
            expect(ctaButton).toHaveClass(
                'block',
                'w-full',
                'text-center',
                'bg-gradient-to-r',
                'from-blue-500',
                'to-blue-600',
                'text-white',
                'px-8',
                'py-4',
                'rounded-xl',
                'font-semibold',
                'text-lg'
            );
        });

        it('renders the "No credit card required" text', () => {
            const freeText = screen.getByText('No credit card required. Get started for free!');
            expect(freeText).toBeInTheDocument();
            expect(freeText).toHaveClass('text-center', 'text-sm', 'text-gray-500');
        });
    });

    describe('Feature Cards Section', () => {
        it('renders the Conversations feature card', () => {
            const conversationsCard = screen.getByText('Conversations');
            expect(conversationsCard).toBeInTheDocument();
            expect(conversationsCard).toHaveClass('text-xl', 'font-semibold', 'mb-2');

            const conversationsDescription = screen.getByText(
                'Chat with AI about your travel preferences and get instant recommendations'
            );
            expect(conversationsDescription).toBeInTheDocument();
        });

        it('renders the Suggestions feature card', () => {
            const suggestionsCard = screen.getByText('Suggestions');
            expect(suggestionsCard).toBeInTheDocument();
            expect(suggestionsCard).toHaveClass('text-xl', 'font-semibold', 'mb-2');

            const suggestionsDescription = screen.getByText(
                'Get personalized suggestions for attractions, restaurants, and activities'
            );
            expect(suggestionsDescription).toBeInTheDocument();
        });

        it('renders the Daily Plans feature card', () => {
            const dailyPlansCard = screen.getByText('Daily Plans');
            expect(dailyPlansCard).toBeInTheDocument();
            expect(dailyPlansCard).toHaveClass('text-xl', 'font-semibold', 'mb-2');

            const dailyPlansDescription = screen.getByText(
                'Receive detailed day-to-day itineraries for your schedule'
            );
            expect(dailyPlansDescription).toBeInTheDocument();
        });

        it('applies correct styling to feature cards', () => {
            const cardTitles = ['Conversations', 'Suggestions', 'Daily Plans'];

            cardTitles.forEach(title => {
                const card = screen.getByText(title).closest('div');
                expect(card).toHaveClass('bg-white', 'p-6', 'rounded-xl', 'shadow-md');
            });
        });
    });

    describe('Footer Section', () => {
        it('renders the powered by text', () => {
            const poweredByText = screen.getByText(
                'Powered by GPT-4.1-nano and intelligent travel planning algorithms'
            );
            expect(poweredByText).toBeInTheDocument();
            expect(poweredByText).toHaveClass('text-gray-500', 'text-sm');
        });
    });

    describe('Responsive Design', () => {
        it('applies responsive grid classes to main content', () => {
            const gridContainer = screen.getByText('Get Started On Your Journey').closest('.grid');
            expect(gridContainer).toHaveClass('md:grid-cols-2', 'gap-8', 'items-center');
        });

        it('applies responsive grid classes to feature cards', () => {
            const featureGrid = screen.getByText('Conversations').closest('.grid');
            expect(featureGrid).toHaveClass('md:grid-cols-3', 'gap-6');
        });
    });

    describe('Accessibility', () => {
        it('has proper heading hierarchy', () => {
            const h1 = screen.getByRole('heading', { level: 1 });
            const h2 = screen.getByRole('heading', { level: 2 });
            const h3Elements = screen.getAllByRole('heading', { level: 3 });

            expect(h1).toBeInTheDocument();
            expect(h2).toBeInTheDocument();
            expect(h3Elements).toHaveLength(3); // Three feature cards
        });

        it('has accessible link text', () => {
            const link = screen.getByRole('link', { name: 'Start Planning Now' });
            expect(link).toBeInTheDocument();
        });
    });

    describe('Component Integration', () => {
        it('integrates with Next.js Link component correctly', () => {
            const link = screen.getByRole('link', { name: 'Start Planning Now' });
            expect(link).toHaveAttribute('href', '/chat');
        });
    });
});