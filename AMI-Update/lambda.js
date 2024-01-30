const AWS = require('aws-sdk');
const ssm = new AWS.SSM();

exports.handler = async (event) => {
    try {
        const params = {
            DocumentName: 'YourAutomationDocument',
            Parameters: {
                'param1': ['value1'],
                'param2': ['value2'],
                // Add any other parameters needed for your Systems Manager action
            },
        };

        const result = await ssm.startAutomationExecution(params).promise();
        console.log('Automation execution started:', result);
    } catch (error) {
        console.error('Error starting automation execution:', error);
        throw error;
    }
};
