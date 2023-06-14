// NLPDocTool
import React, {Component} from 'react';

import states from './../../Constants/States';
// ^ should be able to use this to change the page
// using 

class DocTool extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // maybe to go back and forth between steps
            // since the urls are just /NLPDocTool/step{}
            stepNumber: 0,
        }
    }

    async componentDidMount() {
        try {
            // this is kept here as a template for what posting data function calls look like
            // use props to send along necessary helpers
            // await this.props.postData('/data/save_annotations', {"rows": this.props.loadAnnotations(), "id": this.props.getOptionID()});
            const data = await this.props.getDataWithParams('/documentation', {"id": this.props.getOptionID()});
            
            if (!data.ok) {
                throw Error(data.statusText);
            }

            // this will probably be where we load the model to pass it to NLPDocTool
        } catch (error) {
            console.log(`Unable to mount <Documentation> component. Got error: ${error}`);
        }
    }

    render() {
        // outer div is because apparently you always need a parent div
        return (
            <div id="DocumentationHomePage">
                <div>Hello from documentation!</div>
                <div>Todo: </div>
                <li>link to NLPDocTool home page</li>
                <li>Try to link to other steps</li>
            </div>
        );
    }
}

export default DocTool;