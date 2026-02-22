import { Command } from 'commander';
import { initCommand } from './commands/init';
import { statusCommand } from './commands/status';

const program = new Command();

program
    .name('tracecontext')
    .description('TraceContext CLI - Capture and search developer intent.')
    .version('1.0.0');

program
    .command('init')
    .description('Initialize TraceContext in the current repository.')
    .action(initCommand);

program
    .command('status')
    .description('Check the status of the TraceContext daemon.')
    .action(statusCommand);

program
    .command('search <query>')
    .description('Search for context based on a query.')
    .action((query) => {
        console.log(`Searching for: ${query}`);
        // TODO: Call orchestrator search API
    });

program.parse();
